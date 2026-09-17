from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from app.db import query, transaction
from app.main import app, login_guard
from fastapi.testclient import TestClient
from app.models import Borrow
from app.security import hash_password, verify_password
from app.services import LoanService, overdue_days

def test_TC01_login_logout(client):
    assert client.get('/api/me').json()['role']=='admin'
    assert client.post('/api/logout').status_code==200
    assert client.get('/api/books').status_code==401

def test_TC02_bad_password(client):
    assert client.post('/api/login',json={'username':'admin','password':'wrong'}).status_code==401

def test_TC03_book_crud_search(client,book):
    r=client.post('/api/books',json=book); assert r.status_code==201
    bid=r.json()['id']; book['title']='Python nâng cao'
    assert client.put(f'/api/books/{bid}',json=book).status_code==200
    assert client.get('/api/books?q=PYTHON NÂNG').json()[0]['id']==bid
    assert client.delete(f'/api/books/{bid}').status_code==200
    assert client.get('/api/books?q=NEW').json()==[]

def test_TC04_duplicate_book(client,book):
    client.post('/api/books',json=book)
    assert client.post('/api/books',json=book).status_code==409

def test_TC05_reader_crud(client,reader):
    r=client.post('/api/readers',json=reader); assert r.status_code==201
    rid=r.json()['id']; reader['name']='Tên đã sửa'
    assert client.put(f'/api/readers/{rid}',json=reader).status_code==200
    assert client.get('/api/readers?q=Tên đã sửa').json()[0]['id']==rid
    assert client.delete(f'/api/readers/{rid}').status_code==200

def test_TC06_borrow_return_inventory(client):
    before=next(b for b in client.get('/api/books').json() if b['id']==8)['available']
    r=client.post('/api/loans',json={'book_id':8,'reader_id':4,'days':14}); assert r.status_code==201
    lid=r.json()['id']
    assert next(b for b in client.get('/api/books').json() if b['id']==8)['available']==before-1
    assert client.post(f'/api/loans/{lid}/return').status_code==200
    assert next(b for b in client.get('/api/books').json() if b['id']==8)['available']==before

def test_TC07_out_of_stock(client,book):
    book['total']=0; bid=client.post('/api/books',json=book).json()['id']
    assert client.post('/api/loans',json={'book_id':bid,'reader_id':4,'days':14}).status_code==409

def test_TC08_return_twice(client):
    assert client.post('/api/loans/1/return').status_code==200
    assert client.post('/api/loans/1/return').status_code==409

def test_TC09_nonexistent(client):
    assert client.post('/api/loans',json={'book_id':9999,'reader_id':4}).status_code==404
    assert client.post('/api/loans/9999/return').status_code==404

def test_TC10_overdue_filter(client):
    rows=client.get('/api/loans?status=overdue').json()
    assert len(rows)==1 and rows[0]['id']==1 and rows[0]['overdue_days']==6
    assert client.get('/api/stats').json()['overdue']==1

def test_TC11_no_deactivate_open_loan(client):
    assert client.delete('/api/books/1').status_code==409
    assert client.delete('/api/readers/1').status_code==409

def test_TC12_role_permissions(client,book):
    client.post('/api/login',json={'username':'thuthu','password':'ThuThu@123'})
    assert client.post('/api/books',json=book).status_code==201
    assert client.delete('/api/books/8').status_code==403

def test_TC13_total_below_borrowed(client):
    b=next(b for b in client.get('/api/books').json() if b['id']==1)
    body={k:b[k] for k in ['code','title','author','category','total']};body['total']=0
    assert client.put('/api/books/1',json=body).status_code==409

def test_TC14_inactive_reader(client):
    assert client.delete('/api/readers/4').status_code==200
    assert client.post('/api/loans',json={'book_id':8,'reader_id':4}).status_code==404

def test_TC15_sql_search_literal(client):
    assert client.get('/api/books',params={'q':"' OR 1=1 --"}).json()==[]
    assert client.get('/api/stats').json()['titles']==8

def test_TC16_csrf_header(client):
    client.headers.pop('X-Library-Request')
    assert client.post('/api/loans/1/return').status_code==403

def test_TC17_expired_session(client):
    with transaction() as db: db.execute('UPDATE sessions SET expires_at=0')
    assert client.get('/api/me').status_code==401

def test_TC18_duplicate_reader(client,reader):
    client.post('/api/readers',json=reader)
    assert client.post('/api/readers',json=reader).status_code==409

@pytest.mark.parametrize('days,expected',[(0,422),(1,201),(2,201),(29,201),(30,201),(31,422)])
def test_B01_loan_days(client,days,expected):
    assert client.post('/api/loans',json={'book_id':8,'reader_id':4,'days':days}).status_code==expected

@pytest.mark.parametrize('total,expected',[(-1,422),(0,201),(1,201),(998,201),(999,201),(1000,422)])
def test_B02_book_quantity(client,book,total,expected):
    book['total']=total
    assert client.post('/api/books',json=book).status_code==expected

@pytest.mark.parametrize('length,expected',[(0,422),(1,201),(199,201),(200,201),(201,422)])
def test_B03_title_length(client,book,length,expected):
    book['title']='A'*length
    assert client.post('/api/books',json=book).status_code==expected

def test_B04_reader_limit(client):
    for _ in range(5): assert client.post('/api/loans',json={'book_id':5,'reader_id':4}).status_code==201
    assert client.post('/api/loans',json={'book_id':5,'reader_id':4}).status_code==409

def test_B05_whitespace_title(client,book):
    book['title']='   '
    assert client.post('/api/books',json=book).status_code==422

def test_B06_fractional_quantity(client,book):
    book['total']=1.5
    assert client.post('/api/books',json=book).status_code==422

@pytest.mark.parametrize('offset,expected',[(-1,0),(0,0),(1,1)])
def test_U01_overdue_boundary(offset,expected):
    today=date(2026,9,15)
    assert overdue_days((today-timedelta(days=offset)).isoformat(),today=today)==expected

def test_U02_return_freezes_overdue():
    assert overdue_days('2026-09-10','2026-09-12',today=date(2026,10,1))==2

def test_U03_password_hash():
    stored=hash_password('demo-password')
    assert verify_password('demo-password',stored)
    assert not verify_password('wrong',stored)
    assert stored!=hash_password('demo-password')

def test_I01_concurrent_last_copy(client,book):
    book['total']=1;bid=client.post('/api/books',json=book).json()['id']
    def borrow(reader):
        try:
            LoanService.borrow(Borrow(book_id=bid,reader_id=reader,days=14),1)
            return 201
        except HTTPException as e: return e.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(borrow,[1,2]))
    assert sorted(results)==[201,409]
    assert query('SELECT COUNT(*) AS n FROM loans WHERE book_id=?',(bid,))[0]['n']==1

def test_I02_failed_borrow_no_write(client,book):
    book['total']=0;bid=client.post('/api/books',json=book).json()['id']
    before=len(query('SELECT * FROM loans'))
    assert client.post('/api/loans',json={'book_id':bid,'reader_id':4}).status_code==409
    assert len(query('SELECT * FROM loans'))==before

def test_TC19_static_page(client):
    assert client.get('/').status_code==200
    assert 'lang="vi"' in client.get('/').text
    assert client.get('/static/js/main.js').status_code==200

def test_TC20_statistics(client):
    s=client.get('/api/stats').json()
    assert (s['titles'],s['copies'],s['available'],s['readers'],s['borrowing'],s['overdue'],s['returned'])==(8,29,26,4,3,1,2)

def test_TC21_missing_update(client,book):
    assert client.put('/api/books/999',json=book).status_code==404

def test_TC22_inactive_book(client):
    assert client.delete('/api/books/8').status_code==200
    assert client.post('/api/loans',json={'book_id':8,'reader_id':4}).status_code==404

def test_TC23_loan_filter_options_valid_html(client):
    # Bộ lọc phiếu nằm trong khung HTML của trang loans (app/static/views/loans.html)
    src=client.get('/static/views/loans.html').text
    select=src[src.index('<select id="loan-status">'):src.index('</select>')]
    assert select.count('<option value=')==4 and '</option value=' not in select

def test_TC24_login_lockout(client):
    client.post('/api/logout')
    for _ in range(5): assert client.post('/api/login',json={'username':'admin','password':'wrong'}).status_code==401
    assert client.post('/api/login',json={'username':'admin','password':'Admin@123'}).status_code==429
    login_guard.reset()
    assert client.post('/api/login',json={'username':'admin','password':'Admin@123'}).status_code==200

def test_TC25_user_management(client):
    assert client.get('/api/users').status_code==200
    r=client.post('/api/users',json={'username':'nv01','password':'NhanVien@1','role':'librarian'}); assert r.status_code==201
    uid=r.json()['id']
    assert client.post('/api/users',json={'username':'nv01','password':'NhanVien@1','role':'librarian'}).status_code==409
    assert client.post('/api/users',json={'username':'nv02','password':'short','role':'librarian'}).status_code==422
    assert client.put(f'/api/users/{uid}',json={'role':'admin'}).status_code==200
    assert client.put(f'/api/users/{uid}',json={'active':False}).status_code==200
    assert client.post('/api/login',json={'username':'nv01','password':'NhanVien@1'}).status_code==401
    assert client.put('/api/users/999',json={'role':'admin'}).status_code==404
    assert client.put('/api/users/1',json={'role':'librarian'}).status_code==409

def test_TC26_user_management_admin_only(client):
    client.post('/api/login',json={'username':'thuthu','password':'ThuThu@123'})
    assert client.get('/api/users').status_code==403
    assert client.post('/api/users',json={'username':'nv03','password':'NhanVien@1','role':'admin'}).status_code==403
    assert client.post('/api/backup').status_code==403

def test_TC27_change_password_invalidates_other_sessions(client):
    other=TestClient(app,headers={'X-Library-Request':'1'})
    assert other.post('/api/login',json={'username':'admin','password':'Admin@123'}).status_code==200
    assert client.post('/api/password',json={'current_password':'sai','new_password':'MoiHoanToan1'}).status_code==401
    assert client.post('/api/password',json={'current_password':'Admin@123','new_password':'MoiHoanToan1'}).status_code==200
    assert client.get('/api/me').status_code==200
    assert other.get('/api/me').status_code==401
    assert client.post('/api/login',json={'username':'admin','password':'MoiHoanToan1'}).status_code==200

def test_TC28_extend_loan(client):
    before=next(l for l in client.get('/api/loans').json() if l['id']==2)['due_on']
    r=client.post('/api/loans/2/extend',json={'days':7}); assert r.status_code==200
    assert r.json()['due_on']==(date.fromisoformat(before)+timedelta(days=7)).isoformat()
    assert client.post('/api/loans/2/extend',json={'days':7}).status_code==409
    assert client.post('/api/loans/1/extend',json={'days':7}).status_code==409
    assert client.post('/api/loans/4/extend',json={'days':7}).status_code==409
    assert client.post('/api/loans/999/extend',json={'days':7}).status_code==404
    assert client.post('/api/loans/3/extend',json={'days':31}).status_code==422

def test_TC29_export_csv(client):
    r=client.get('/api/export/loans.csv'); assert r.status_code==200
    assert r.headers['content-type'].startswith('text/csv') and 'attachment' in r.headers['content-disposition']
    lines=r.text.lstrip('﻿').splitlines()
    assert lines[0].startswith('Phiếu,Mã sách') and len(lines)==6
    assert len(client.get('/api/export/books.csv').text.splitlines())==9
    assert client.get('/api/export/nope.csv').status_code==404

def test_TC30_backup(client,tmp_path):
    r=client.post('/api/backup'); assert r.status_code==200
    files=list((tmp_path/'backups').glob('test-*.db'))
    assert r.json()['file'] in [f.name for f in files]
    assert query("SELECT COUNT(*) AS n FROM sqlite_master")[0]['n']>0
    import sqlite3
    assert sqlite3.connect(tmp_path/'backups'/r.json()['file']).execute('SELECT COUNT(*) FROM books').fetchone()[0]==8

def test_TC31_migration_adds_columns(tmp_path,monkeypatch):
    import sqlite3
    from app.db import initialize
    old=tmp_path/'old.db'
    sqlite3.connect(old).executescript("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL);CREATE TABLE loans(id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, reader_id INTEGER NOT NULL, created_by INTEGER NOT NULL, borrowed_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT, returned_by INTEGER);INSERT INTO users VALUES(1,'a','x$y','admin');")
    monkeypatch.setenv('LIBRARY_DB',str(old)); initialize()
    assert query('SELECT active FROM users')[0]['active']==1
    assert 'extensions' in [c['name'] for c in query('PRAGMA table_info(loans)')]

def test_TC32_pagination(client):
    for i in range(25): assert client.post('/api/readers',json={'code':f'P{i:03}','name':f'Độc giả phân trang {i}','phone':''}).status_code==201
    r=client.get('/api/readers?page=1&size=10').json()
    assert (r['total'],r['pages'],r['page'],len(r['items']))==(29,3,1,10)
    assert r['items'][0]['code']=='P024'
    last=client.get('/api/readers?page=3&size=10').json(); assert len(last['items'])==9
    assert client.get('/api/readers?page=99&size=10').json()['page']==3
    assert client.get('/api/readers?page=0').status_code==422 and client.get('/api/readers?size=101').status_code==422
    assert isinstance(client.get('/api/readers').json(),list) and len(client.get('/api/readers').json())==29
    q=client.get('/api/readers?q=PHÂN TRANG 1&page=1&size=5').json(); assert q['total']==11 and len(q['items'])==5
    l=client.get('/api/loans?status=open&page=1&size=1').json(); assert l['total']==2 and l['items'][0]['status']=='open'
    assert client.get('/api/loans?status=bogus').status_code==422

def test_TC33_frontend_not_cached(client):
    assert client.get('/').headers['cache-control']=='no-cache'
    assert client.get('/static/js/main.js').headers['cache-control']=='no-cache'
    assert 'js/main.js?v=' in client.get('/').text

def test_TC34_ui_paths_serve_spa(client):
    for path in ['/', '/books', '/readers', '/loans', '/loans/overdue', '/users']:
        r=client.get(path); assert r.status_code==200 and 'id="app-view"' in r.text, path
    assert client.get('/nope').status_code==404 and client.get('/loans/nope').status_code==404
    assert client.get('/openapi.json').status_code==200

def test_TC35_not_found_page(client):
    r=client.get('/khong-co',headers={'accept':'text/html'})
    assert r.status_code==404 and 'Không tìm thấy trang' in r.text and 'text/html' in r.headers['content-type']
    r=client.get('/api/khong-co',headers={'accept':'text/html'})
    assert r.status_code==404 and r.headers['content-type'].startswith('application/json')
    assert client.get('/khong-co').json()['detail']

def test_TC36_seed_demo(tmp_path, monkeypatch):
    import seed as seed_module
    db=tmp_path/'demo.db'
    assert seed_module.main(['--demo','--db',str(db)])==0
    assert seed_module.main(['--demo','--db',str(db)])==1          # không ghi đè khi đã có
    assert seed_module.main(['--demo','--db',str(db),'--force'])==0
    monkeypatch.setenv('LIBRARY_DB',str(db))
    counts={t:query(f'SELECT COUNT(*) AS n FROM {t}')[0]['n'] for t in ('users','books','readers','loans')}
    assert counts['books']>=60 and counts['readers']==60 and counts['loans']>200
    assert query('SELECT COUNT(*) AS n FROM loans WHERE returned_on IS NULL AND due_on<date("now")')[0]['n']>0
    assert query('SELECT MAX(c) AS m FROM (SELECT COUNT(*) c FROM loans WHERE returned_on IS NULL GROUP BY reader_id)')[0]['m']<=5
    assert query('SELECT COUNT(*) AS n FROM books b WHERE (SELECT COUNT(*) FROM loans l WHERE l.book_id=b.id AND l.returned_on IS NULL)>b.total')[0]['n']==0
    login_guard.reset()
    with TestClient(app,headers={'X-Library-Request':'1'}) as c:
        assert c.post('/api/login',json={'username':'admin','password':'Admin@123'}).status_code==200
        assert c.get('/api/books?page=1&size=20').json()['pages']>=3
        assert c.get('/api/stats').json()['overdue']>0
