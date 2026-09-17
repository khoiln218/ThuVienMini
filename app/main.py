import csv
import io
import os
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import date
from math import ceil
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from .db import backup, initialize, query, transaction
from .models import Login, Book, Reader, Borrow, Extend, UserCreate, UserUpdate, PasswordChange
from .security import hash_password, verify_password, token_hash, LoginGuard
from .services import LoanService, overdue_days

login_guard = LoginGuard()

@asynccontextmanager
async def lifespan(app):
    initialize()
    if os.environ.get('LIBRARY_BACKUP', '1') != '0':
        backup()  # sao lưu tự động mỗi lần khởi động, giữ 10 bản gần nhất
    yield

app = FastAPI(title='Thư viện mini • Nhóm 1', lifespan=lifespan)
STATIC = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=STATIC), name='static')

@app.middleware('http')
async def no_stale_frontend(request: Request, call_next):
    # Trang và file tĩnh luôn được trình duyệt kiểm tra lại (ETag) thay vì dùng bản cache cũ sau khi cập nhật code
    response = await call_next(request)
    if request.url.path == '/' or request.url.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-cache'
    return response

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    # Người dùng gõ URL lạ trên trình duyệt → trang 404 có giao diện; API và file tĩnh vẫn trả JSON để client xử lý
    if request.url.path.startswith(('/api/', '/static/')) or 'text/html' not in request.headers.get('accept', ''):
        return JSONResponse(status_code=404, content={'detail': getattr(exc, 'detail', 'Không tìm thấy')})
    return FileResponse(STATIC / 'views/404.html', status_code=404)

@app.exception_handler(sqlite3.IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={'detail': 'Mã đã tồn tại hoặc dữ liệu vi phạm ràng buộc'})

def current_user(request: Request):
    token = request.cookies.get('session', '')
    rows = query('SELECT u.id,u.username,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>? AND u.active=1', (token_hash(token), int(time.time())))
    if not rows:
        raise HTTPException(401, 'Vui lòng đăng nhập')
    if request.method not in ('GET', 'HEAD', 'OPTIONS') and request.headers.get('X-Library-Request') != '1':
        raise HTTPException(403, 'Thiếu xác thực yêu cầu')
    return rows[0]

def admin(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Chỉ quản trị viên được thực hiện thao tác này')
    return user

# Đường dẫn giao diện (SPA dùng History API): server trả index.html, JS đọc location.pathname để mở đúng màn hình
UI_PAGES = ('dashboard', 'books', 'readers', 'loans', 'users')

@app.get('/')
def home():
    return FileResponse(STATIC / 'index.html')

@app.get('/{page}')
def ui_page(page: str):
    if page not in UI_PAGES:
        raise HTTPException(404, 'Không có trang này')
    return FileResponse(STATIC / 'index.html')

@app.get('/loans/{status}')
def ui_loans(status: str):
    if status not in LOAN_STATUS:
        raise HTTPException(404, 'Không có trang này')
    return FileResponse(STATIC / 'index.html')

@app.post('/api/login')
def login(data: Login, response: Response, request: Request):
    if request.headers.get('X-Library-Request') != '1':
        raise HTTPException(403, 'Yêu cầu không hợp lệ')
    key = f"{data.username.casefold()}@{request.client.host if request.client else ''}"
    wait = login_guard.check(key)
    if wait:
        raise HTTPException(429, f'Sai mật khẩu quá nhiều lần, thử lại sau {max(1, wait // 60)} phút')
    rows = query('SELECT * FROM users WHERE username=? AND active=1', (data.username,))
    if not rows or not verify_password(data.password, rows[0]['password_hash']):
        login_guard.fail(key)
        raise HTTPException(401, 'Tên đăng nhập hoặc mật khẩu không đúng')
    login_guard.succeed(key)
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

@app.post('/api/password')
def change_password(data: PasswordChange, request: Request, user=Depends(current_user)):
    with transaction() as db:
        stored = db.execute('SELECT password_hash FROM users WHERE id=?', (user['id'],)).fetchone()[0]
        if not verify_password(data.current_password, stored):
            raise HTTPException(401, 'Mật khẩu hiện tại không đúng')
        db.execute('UPDATE users SET password_hash=? WHERE id=?', (hash_password(data.new_password), user['id']))
        # Hủy các phiên khác của cùng tài khoản, giữ phiên đang dùng
        db.execute('DELETE FROM sessions WHERE user_id=? AND token_hash<>?', (user['id'], token_hash(request.cookies.get('session', ''))))
    return {'message': 'Đã đổi mật khẩu'}

@app.get('/api/users')
def users(user=Depends(admin)):
    return query('SELECT id,username,role,active FROM users ORDER BY id')

@app.post('/api/users', status_code=201)
def add_user(data: UserCreate, user=Depends(admin)):
    with transaction() as db:
        cur = db.execute('INSERT INTO users(username,password_hash,role) VALUES(?,?,?)', (data.username, hash_password(data.password), data.role))
    return {'id': cur.lastrowid, 'message': 'Đã tạo tài khoản'}

@app.put('/api/users/{record_id}')
def edit_user(record_id: int, data: UserUpdate, user=Depends(admin)):
    changes = {}
    if data.role is not None: changes['role'] = data.role
    if data.active is not None: changes['active'] = int(data.active)
    if data.password is not None: changes['password_hash'] = hash_password(data.password)
    if not changes:
        raise HTTPException(422, 'Không có gì để cập nhật')
    with transaction() as db:
        if not db.execute('SELECT id FROM users WHERE id=?', (record_id,)).fetchone():
            raise HTTPException(404, 'Không tìm thấy tài khoản')
        if record_id == user['id'] and (changes.get('role') == 'librarian' or changes.get('active') == 0):
            raise HTTPException(409, 'Không thể tự hạ quyền hoặc tự ngừng tài khoản đang đăng nhập')
        if changes.get('active') == 0 or changes.get('role') == 'librarian':
            admins = db.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND active=1 AND id<>?", (record_id,)).fetchone()[0]
            if not admins:
                raise HTTPException(409, 'Phải còn ít nhất một quản trị viên hoạt động')
        db.execute(f"UPDATE users SET {','.join(k+'=?' for k in changes)} WHERE id=?", (*changes.values(), record_id))
        if changes.get('active') == 0 or 'password_hash' in changes:
            db.execute('DELETE FROM sessions WHERE user_id=?', (record_id,))
    return {'message': 'Đã cập nhật tài khoản'}

def paginated(select, source, order, params, page, size):
    """Không có `page`: trả toàn bộ danh sách (dùng cho hộp chọn, xuất CSV, test).
    Có `page`: trả {items,total,page,size,pages} với LIMIT/OFFSET ở SQL."""
    if page is None:
        return query(f'{select} {source} {order}', params)
    total = query(f'SELECT COUNT(*) AS n {source}', params)[0]['n']
    pages = max(1, ceil(total / size))
    page = min(page, pages)
    items = query(f'{select} {source} {order} LIMIT ? OFFSET ?', (*params, size, (page - 1) * size))
    return {'items': items, 'total': total, 'page': page, 'size': size, 'pages': pages}

PAGE = Query(default=None, ge=1)
SIZE = Query(default=20, ge=1, le=100)

@app.get('/api/books')
def books(q: str = '', page: int | None = PAGE, size: int = SIZE, user=Depends(current_user)):
    return paginated('SELECT b.*, b.total-(SELECT COUNT(*) FROM loans l WHERE l.book_id=b.id AND l.returned_on IS NULL) AS available',
        "FROM books b WHERE b.active=1 AND instr(casefold(b.code||' '||b.barcode||' '||b.title||' '||b.author||' '||b.category), ?)>0",
        'ORDER BY b.id DESC', (q.strip().casefold(),), page, size)

@app.get('/api/readers')
def readers(q: str = '', page: int | None = PAGE, size: int = SIZE, user=Depends(current_user)):
    return paginated('SELECT *', "FROM readers WHERE active=1 AND instr(casefold(name||' '||code||' '||phone), ?)>0",
        'ORDER BY id DESC', (q.strip().casefold(),), page, size)

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

# Điều kiện trạng thái phiếu tính ngay trong SQL theo ngày hiện tại (?), khớp với overdue_days()
LOAN_STATUS = {'all': '1=1', 'returned': 'l.returned_on IS NOT NULL',
               'overdue': 'l.returned_on IS NULL AND l.due_on < ?', 'open': 'l.returned_on IS NULL AND l.due_on >= ?'}

@app.get('/api/loans')
def loans(status: str = 'all', page: int | None = PAGE, size: int = SIZE, user=Depends(current_user)):
    if status not in LOAN_STATUS:
        raise HTTPException(422, 'Trạng thái không hợp lệ')
    params = (date.today().isoformat(),) if '?' in LOAN_STATUS[status] else ()
    result = paginated('SELECT l.*,b.title,b.code AS book_code,r.name,r.code AS reader_code,u.username AS staff',
        f'FROM loans l JOIN books b ON l.book_id=b.id JOIN readers r ON l.reader_id=r.id JOIN users u ON l.created_by=u.id WHERE {LOAN_STATUS[status]}',
        'ORDER BY l.id DESC', params, page, size)
    for row in (result['items'] if page else result):
        row['overdue_days'] = overdue_days(row['due_on'], row['returned_on'])
        row['status'] = 'returned' if row['returned_on'] else ('overdue' if row['overdue_days'] else 'open')
    return result

@app.post('/api/loans', status_code=201)
def borrow(data: Borrow, user=Depends(current_user)):
    return LoanService.borrow(data, user['id'])

@app.post('/api/loans/{loan_id}/return')
def return_book(loan_id: int, user=Depends(current_user)):
    return LoanService.return_book(loan_id, user['id'])

@app.post('/api/loans/{loan_id}/extend')
def extend_loan(loan_id: int, data: Extend, user=Depends(current_user)):
    return LoanService.extend(loan_id, data.days)

EXPORTS = {
    'books': (['Mã sách', 'Mã vạch', 'Tên sách', 'Tác giả', 'Thể loại', 'Tổng bản', 'Có sẵn'], ('code', 'barcode', 'title', 'author', 'category', 'total', 'available')),
    'readers': (['Mã độc giả', 'Họ tên', 'Điện thoại'], ('code', 'name', 'phone')),
    'loans': (['Phiếu', 'Mã sách', 'Tên sách', 'Mã độc giả', 'Độc giả', 'Ngày mượn', 'Hạn trả', 'Ngày trả', 'Quá hạn (ngày)', 'Trạng thái', 'Gia hạn', 'Thủ thư'],
              ('id', 'book_code', 'title', 'reader_code', 'name', 'borrowed_on', 'due_on', 'returned_on', 'overdue_days', 'status', 'extensions', 'staff')),
}

@app.get('/api/export/{resource}.csv')
def export_csv(resource: str, user=Depends(current_user)):
    if resource not in EXPORTS:
        raise HTTPException(404, 'Không có tài nguyên')
    header, keys = EXPORTS[resource]
    # Gọi trực tiếp (không qua FastAPI) nên phải truyền page/size tường minh; page=None → toàn bộ
    rows = {'books': books, 'readers': readers, 'loans': loans}[resource](page=None, size=20, user=user)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(['' if row[k] is None else row[k] for k in keys])
    # BOM để Excel trên Windows nhận đúng UTF-8 tiếng Việt
    content = '\ufeff' + buffer.getvalue()
    filename = f"{resource}-{time.strftime('%Y%m%d')}.csv"
    return StreamingResponse(iter([content]), media_type='text/csv; charset=utf-8', headers={'Content-Disposition': f'attachment; filename="{filename}"'})

@app.post('/api/backup')
def make_backup(user=Depends(admin)):
    target = backup()
    return {'message': 'Đã sao lưu', 'file': target.name}

@app.get('/api/stats')
def stats(user=Depends(current_user)):
    today = date.today().isoformat()
    inventory = query('SELECT COUNT(*) AS titles, COALESCE(SUM(total),0) AS copies FROM books WHERE active=1')[0]
    borrowing = query('SELECT COUNT(*) AS n FROM loans l JOIN books b ON b.id=l.book_id WHERE l.returned_on IS NULL AND b.active=1')[0]['n']
    counts = query('SELECT SUM(returned_on IS NULL) AS borrowing, SUM(returned_on IS NULL AND due_on<?) AS overdue, SUM(returned_on IS NOT NULL) AS returned FROM loans', (today,))[0]
    return {'titles': inventory['titles'], 'copies': inventory['copies'],
        'available': inventory['copies'] - borrowing, 'readers': query('SELECT COUNT(*) AS n FROM readers WHERE active=1')[0]['n'],
        'borrowing': counts['borrowing'] or 0, 'overdue': counts['overdue'] or 0, 'returned': counts['returned'] or 0,
        'top_books': query('SELECT b.title,COUNT(*) AS count FROM loans l JOIN books b ON l.book_id=b.id GROUP BY b.id ORDER BY count DESC,b.id LIMIT 5')}
