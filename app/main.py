import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .db import initialize, query, transaction
from .models import Login, Book, Reader, Borrow
from .security import verify_password, token_hash
from .services import LoanService, overdue_days

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app = FastAPI(title='Thư viện mini • Nhóm 1', lifespan=lifespan)
STATIC = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=STATIC), name='static')

@app.exception_handler(sqlite3.IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={'detail': 'Mã đã tồn tại hoặc dữ liệu vi phạm ràng buộc'})

def current_user(request: Request):
    token = request.cookies.get('session', '')
    rows = query('SELECT u.id,u.username,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?', (token_hash(token), int(time.time())))
    if not rows:
        raise HTTPException(401, 'Vui lòng đăng nhập')
    if request.method not in ('GET', 'HEAD', 'OPTIONS') and request.headers.get('X-Library-Request') != '1':
        raise HTTPException(403, 'Thiếu xác thực yêu cầu')
    return rows[0]

def admin(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Chỉ quản trị viên được ngừng hoạt động bản ghi')
    return user

@app.get('/')
def home():
    return FileResponse(STATIC / 'index.html')

@app.post('/api/login')
def login(data: Login, response: Response, request: Request):
    if request.headers.get('X-Library-Request') != '1':
        raise HTTPException(403, 'Yêu cầu không hợp lệ')
    rows = query('SELECT * FROM users WHERE username=?', (data.username,))
    if not rows or not verify_password(data.password, rows[0]['password_hash']):
        raise HTTPException(401, 'Tên đăng nhập hoặc mật khẩu không đúng')
    token = secrets.token_urlsafe(32)
    with transaction() as db:
        db.execute('DELETE FROM sessions WHERE expires_at<=?', (int(time.time()),))
        db.execute('INSERT INTO sessions VALUES(?,?,?)', (token_hash(token), rows[0]['id'], int(time.time()) + 28800))
    response.set_cookie('session', token, httponly=True, samesite='strict', max_age=28800)
    return {'username': rows[0]['username'], 'role': rows[0]['role']}

@app.get('/api/me')
def me(user=Depends(current_user)):
    return user

@app.post('/api/logout')
def logout(request: Request, response: Response, user=Depends(current_user)):
    with transaction() as db:
        db.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash(request.cookies.get('session', '')),))
    response.delete_cookie('session')
    return {'message': 'Đã đăng xuất'}

@app.get('/api/books')
def books(q: str = '', user=Depends(current_user)):
    rows = query('SELECT b.*, b.total-(SELECT COUNT(*) FROM loans l WHERE l.book_id=b.id AND l.returned_on IS NULL) AS available FROM books b WHERE active=1 ORDER BY b.id DESC')
    term = q.strip().casefold()
    return [r for r in rows if term in ' '.join(str(r[k]) for k in ('code','title','author','category')).casefold()]

@app.get('/api/readers')
def readers(q: str = '', user=Depends(current_user)):
    rows = query('SELECT * FROM readers WHERE active=1 ORDER BY id DESC')
    return [r for r in rows if q.strip().casefold() in (r['name']+' '+r['code']+' '+r['phone']).casefold()]

def save_record(table, data, record_id=None):
    values = data.model_dump()
    with transaction() as db:
        if record_id is not None:
            if not db.execute(f'SELECT id FROM {table} WHERE id=? AND active=1', (record_id,)).fetchone():
                raise HTTPException(404, 'Không tìm thấy bản ghi')
            if table == 'books':
                used = db.execute('SELECT COUNT(*) FROM loans WHERE book_id=? AND returned_on IS NULL', (record_id,)).fetchone()[0]
                if values['total'] < used:
                    raise HTTPException(409, 'Tổng số bản không được nhỏ hơn số đang mượn')
            db.execute(f"UPDATE {table} SET {','.join(k+'=?' for k in values)} WHERE id=?", (*values.values(), record_id))
        else:
            cur = db.execute(f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", tuple(values.values()))
            record_id = cur.lastrowid
    return {'id': record_id, 'message': 'Đã lưu'}

@app.post('/api/books', status_code=201)
def add_book(data: Book, user=Depends(current_user)):
    return save_record('books', data)

@app.put('/api/books/{record_id}')
def edit_book(record_id: int, data: Book, user=Depends(current_user)):
    return save_record('books', data, record_id)

@app.post('/api/readers', status_code=201)
def add_reader(data: Reader, user=Depends(current_user)):
    return save_record('readers', data)

@app.put('/api/readers/{record_id}')
def edit_reader(record_id: int, data: Reader, user=Depends(current_user)):
    return save_record('readers', data, record_id)

@app.delete('/api/{resource}/{record_id}')
def deactivate(resource: str, record_id: int, user=Depends(admin)):
    if resource not in ('books', 'readers'):
        raise HTTPException(404, 'Không có tài nguyên')
    column = 'book_id' if resource == 'books' else 'reader_id'
    with transaction() as db:
        if not db.execute(f'SELECT id FROM {resource} WHERE id=? AND active=1', (record_id,)).fetchone():
            raise HTTPException(404, 'Không tìm thấy bản ghi')
        if db.execute(f'SELECT 1 FROM loans WHERE {column}=? AND returned_on IS NULL', (record_id,)).fetchone():
            raise HTTPException(409, 'Còn phiếu chưa trả, không thể ngừng hoạt động')
        db.execute(f'UPDATE {resource} SET active=0 WHERE id=?', (record_id,))
    return {'message': 'Đã ngừng hoạt động, lịch sử vẫn được giữ'}

@app.get('/api/loans')
def loans(status: str = 'all', user=Depends(current_user)):
    rows = query('SELECT l.*,b.title,b.code AS book_code,r.name,r.code AS reader_code,u.username AS staff FROM loans l JOIN books b ON l.book_id=b.id JOIN readers r ON l.reader_id=r.id JOIN users u ON l.created_by=u.id ORDER BY l.id DESC')
    for row in rows:
        row['overdue_days'] = overdue_days(row['due_on'], row['returned_on'])
        row['status'] = 'returned' if row['returned_on'] else ('overdue' if row['overdue_days'] else 'open')
    return [r for r in rows if status == 'all' or r['status'] == status]

@app.post('/api/loans', status_code=201)
def borrow(data: Borrow, user=Depends(current_user)):
    return LoanService.borrow(data, user['id'])

@app.post('/api/loans/{loan_id}/return')
def return_book(loan_id: int, user=Depends(current_user)):
    return LoanService.return_book(loan_id, user['id'])

@app.get('/api/stats')
def stats(user=Depends(current_user)):
    book_rows = books(user=user)
    loan_rows = loans(user=user)
    return {'titles': len(book_rows), 'copies': sum(b['total'] for b in book_rows),
        'available': sum(b['available'] for b in book_rows), 'readers': len(readers(user=user)),
        'borrowing': sum(l['returned_on'] is None for l in loan_rows),
        'overdue': sum(l['status'] == 'overdue' for l in loan_rows),
        'returned': sum(l['returned_on'] is not None for l in loan_rows),
        'top_books': query('SELECT b.title,COUNT(*) AS count FROM loans l JOIN books b ON l.book_id=b.id GROUP BY b.id ORDER BY count DESC,b.id LIMIT 5')}
