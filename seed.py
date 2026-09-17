"""Khởi tạo dữ liệu demo một lần; không xóa hay ghi đè dữ liệu hiện có."""
from datetime import date, timedelta
from app.db import initialize, transaction
from app.security import hash_password

def seed():
    initialize()
    with transaction() as db:
        if db.execute('SELECT COUNT(*) FROM users').fetchone()[0]:
            print('Database already populated; existing data preserved.')
            return
        db.executemany('INSERT INTO users(username,password_hash,role) VALUES(?,?,?)', [
            ('admin', hash_password('Admin@123'), 'admin'),
            ('thuthu', hash_password('ThuThu@123'), 'librarian')])
        books=[('S001','Dế Mèn phiêu lưu ký','Tô Hoài','Văn học',5),('S002','Tôi thấy hoa vàng trên cỏ xanh','Nguyễn Nhật Ánh','Văn học',4),('S003','Lập trình Python cơ bản','Nhóm biên soạn','Tin học',3),('S004','Cơ sở dữ liệu','Nhóm biên soạn','Tin học',4),('S005','Nhập môn Công nghệ Phần mềm','Nhóm biên soạn','Tin học',6),('S006','Toán rời rạc','Nhóm biên soạn','Toán học',2),('S007','Kỹ năng học tập đại học','Nhóm biên soạn','Kỹ năng',3),('S008','Lịch sử Việt Nam nhập môn','Nhóm biên soạn','Lịch sử',2)]
        db.executemany('INSERT INTO books(code,title,author,category,total) VALUES(?,?,?,?,?)',books)
        db.executemany('INSERT INTO readers(code,name,phone) VALUES(?,?,?)', [('DG001','Nguyễn Minh An','0900000001'),('DG002','Trần Hà Linh','0900000002'),('DG003','Lê Hoàng Nam','0900000003'),('DG004','Phạm Ngọc Mai','0900000004')])
        today=date.today()
        for book,reader,start,due,returned in [(1,1,-20,-6,None),(2,2,-4,10,None),(3,3,-8,6,None),(4,4,-25,-11,-13),(1,2,-30,-16,-15)]:
            db.execute('INSERT INTO loans(book_id,reader_id,created_by,borrowed_on,due_on,returned_on,returned_by) VALUES(?,?,?,?,?,?,?)',(book,reader,2,(today+timedelta(days=start)).isoformat(),(today+timedelta(days=due)).isoformat(),(today+timedelta(days=returned)).isoformat() if returned is not None else None,2 if returned is not None else None))
    print('Demo ready: 2 users, 8 books, 4 readers, 5 loans. Fictional data only.')

if __name__=='__main__': seed()
