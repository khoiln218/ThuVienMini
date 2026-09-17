from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from app.db import query, transaction
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
    assert client.get('/static/app.js').status_code==200

def test_TC20_statistics(client):
    s=client.get('/api/stats').json()
    assert (s['titles'],s['copies'],s['available'],s['readers'],s['borrowing'],s['overdue'],s['returned'])==(8,29,26,4,3,1,2)

def test_TC21_missing_update(client,book):
    assert client.put('/api/books/999',json=book).status_code==404

def test_TC22_inactive_book(client):
    assert client.delete('/api/books/8').status_code==200
    assert client.post('/api/loans',json={'book_id':8,'reader_id':4}).status_code==404
