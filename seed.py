"""Khởi tạo dữ liệu.

    python seed.py                  # dữ liệu mẫu nhỏ vào data/library.db (hoặc $LIBRARY_DB); không xóa hay ghi đè dữ liệu hiện có
    python seed.py --demo           # CSDL demo lớn riêng tại data/demo.db để trình diễn phân trang, thống kê, lọc quá hạn
    python seed.py --demo --force   # tạo lại demo từ đầu;  --db để đổi đường dẫn, --seed để đổi bộ dữ liệu

Chạy server với CSDL demo:  LIBRARY_DB=data/demo.db python -m uvicorn app.main:app --port 8001
(Windows PowerShell: $env:LIBRARY_DB="data\\demo.db")

Dữ liệu hư cấu. Demo lớn sinh ngẫu nhiên với hạt giống cố định nên mỗi lần chạy cho kết quả giống nhau.
Tài khoản: admin/Admin@123, thuthu/ThuThu@123; bản demo thêm thuthu2/ThuThu@123 và cu_nhan_vien/ThuThu@123 (đã ngừng).
"""
import argparse
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from app.db import initialize, transaction
from app.security import hash_password

ROOT = Path(__file__).resolve().parent


def seed():
    """Dữ liệu mẫu nhỏ cho bản nộp và test; chỉ tạo khi bảng users còn trống."""
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


# ======================= CSDL demo lớn (--demo) =======================

TITLES = {
    'Văn học': ['Dế Mèn phiêu lưu ký', 'Tôi thấy hoa vàng trên cỏ xanh', 'Số đỏ', 'Tắt đèn', 'Chí Phèo', 'Vợ nhặt',
                'Mắt biếc', 'Cho tôi xin một vé đi tuổi thơ', 'Đất rừng phương Nam', 'Những ngày thơ ấu', 'Truyện Kiều',
                'Lão Hạc', 'Bỉ vỏ', 'Hai đứa trẻ', 'Sống mòn', 'Nỗi buồn chiến tranh', 'Cánh đồng bất tận', 'Mùa lá rụng trong vườn'],
    'Tin học': ['Lập trình Python cơ bản', 'Cơ sở dữ liệu', 'Nhập môn Công nghệ Phần mềm', 'Cấu trúc dữ liệu và giải thuật',
                'Mạng máy tính', 'Hệ điều hành', 'Lập trình web với FastAPI', 'Kiểm thử phần mềm', 'Kiến trúc máy tính',
                'Trí tuệ nhân tạo nhập môn', 'Lập trình hướng đối tượng với Java', 'Phân tích thiết kế hệ thống', 'An toàn thông tin',
                'Học máy cơ bản', 'Git và làm việc nhóm', 'SQL cho người mới bắt đầu'],
    'Toán học': ['Toán rời rạc', 'Đại số tuyến tính', 'Giải tích 1', 'Giải tích 2', 'Xác suất thống kê', 'Phương pháp tính',
                 'Lý thuyết đồ thị', 'Tối ưu hóa'],
    'Kỹ năng': ['Kỹ năng học tập đại học', 'Kỹ năng thuyết trình', 'Quản lý thời gian', 'Tư duy phản biện', 'Kỹ năng viết báo cáo',
                'Làm việc nhóm hiệu quả'],
    'Lịch sử': ['Lịch sử Việt Nam nhập môn', 'Đại Việt sử ký toàn thư (tuyển)', 'Lịch sử thế giới cận đại', 'Việt Nam sử lược',
                'Lịch sử khoa học kỹ thuật'],
    'Kinh tế': ['Kinh tế học vi mô', 'Kinh tế học vĩ mô', 'Nguyên lý kế toán', 'Marketing căn bản', 'Quản trị học'],
    'Ngoại ngữ': ['Tiếng Anh giao tiếp', 'Ngữ pháp tiếng Anh thực hành', 'Tiếng Anh chuyên ngành CNTT', 'IELTS Reading', 'Tiếng Nhật sơ cấp'],
}
AUTHORS = ['Tô Hoài', 'Nguyễn Nhật Ánh', 'Vũ Trọng Phụng', 'Ngô Tất Tố', 'Nam Cao', 'Kim Lân', 'Đoàn Giỏi', 'Nguyên Hồng',
           'Nguyễn Du', 'Bảo Ninh', 'Nguyễn Ngọc Tư', 'Ma Văn Kháng', 'Nhóm biên soạn', 'Nhóm biên soạn', 'Nhóm biên soạn',
           'Trần Văn Minh', 'Lê Thị Hạnh', 'Phạm Quang Huy', 'Nguyễn Thu Trang', 'Hoàng Anh Tuấn']
HO = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
DEM = ['Văn', 'Thị', 'Minh', 'Hồng', 'Thu', 'Quốc', 'Ngọc', 'Hải', 'Thanh', 'Đức', 'Gia', 'Bảo', 'Khánh', 'Phương', 'Anh']
TEN = ['An', 'Bình', 'Chi', 'Dũng', 'Hà', 'Hiếu', 'Hương', 'Khoa', 'Lan', 'Linh', 'Long', 'Mai', 'Nam', 'Nga', 'Phúc',
       'Quân', 'Quỳnh', 'Sơn', 'Thảo', 'Trang', 'Trung', 'Tú', 'Tùng', 'Uyên', 'Vy', 'Yến', 'Đạt', 'Huy', 'Ngân', 'Nhi']


def seed_demo(db_path: Path, today: date, seed: int = 2026):
    """Tạo CSDL demo lớn tại db_path. Trả về (số bản ghi từng bảng, thống kê phiếu)."""
    os.environ['LIBRARY_DB'] = str(db_path)
    rng = random.Random(seed)
    initialize()
    with transaction() as db:
        if db.execute('SELECT COUNT(*) FROM users').fetchone()[0]:
            raise SystemExit(f'{db_path} đã có dữ liệu; dùng --force để tạo lại.')

        # ---- Tài khoản ----
        users = [('admin', 'Admin@123', 'admin', 1), ('thuthu', 'ThuThu@123', 'librarian', 1),
                 ('thuthu2', 'ThuThu@123', 'librarian', 1), ('cu_nhan_vien', 'ThuThu@123', 'librarian', 0)]
        db.executemany('INSERT INTO users(username,password_hash,role,active) VALUES(?,?,?,?)',
                       [(u, hash_password(p), r, a) for u, p, r, a in users])
        staff_ids = [1, 2, 3]

        # ---- Sách ----
        books = []  # (id, total)
        n = 0
        for category, titles in TITLES.items():
            for title in titles:
                n += 1
                total = rng.choice([1, 2, 2, 3, 3, 4, 5, 6, 8])
                author = rng.choice(AUTHORS) if category != 'Văn học' else AUTHORS[(n - 1) % 12]
                active = 0 if rng.random() < 0.05 else 1
                db.execute('INSERT INTO books(code,title,author,category,total,active) VALUES(?,?,?,?,?,?)',
                           (f'S{n:03}', title, author, category, total, active))
                if active:
                    books.append((n, total))

        # ---- Độc giả ----
        readers = []
        for i in range(1, 61):
            name = f'{rng.choice(HO)} {rng.choice(DEM)} {rng.choice(TEN)}'
            phone = '' if rng.random() < 0.15 else '09' + ''.join(rng.choice('0123456789') for _ in range(8))
            active = 0 if rng.random() < 0.05 else 1
            db.execute('INSERT INTO readers(code,name,phone,active) VALUES(?,?,?,?)', (f'DG{i:03}', name, phone, active))
            if active:
                readers.append(i)

        # ---- Phiếu mượn trong 180 ngày gần nhất ----
        open_by_book = {b: 0 for b, _ in books}
        open_by_reader = {r: 0 for r in readers}
        total_by_book = dict(books)
        stats = {'returned': 0, 'late_returned': 0, 'open': 0, 'overdue': 0, 'extended': 0}
        for _ in range(260):
            book = rng.choice(books)[0]
            reader = rng.choice(readers)
            borrowed = today - timedelta(days=rng.randint(0, 180))
            days = rng.choice([7, 14, 14, 14, 21, 30])
            due = borrowed + timedelta(days=days)
            extensions = 0
            if rng.random() < 0.12 and due >= today - timedelta(days=60):
                due += timedelta(days=rng.choice([7, 14]))
                extensions = 1
            # Phiếu cũ thường đã trả; phiếu mới có thể còn mở
            returned = None
            age = (today - borrowed).days
            if age > 45 or (age > days and rng.random() < 0.7) or (age <= days and rng.random() < 0.25):
                late = rng.random() < 0.2
                returned = min(today, due + timedelta(days=rng.randint(1, 20)) if late else borrowed + timedelta(days=rng.randint(1, max(1, days))))
                if returned < borrowed:
                    returned = borrowed
            if returned is None:
                if open_by_book[book] >= total_by_book[book] or open_by_reader[reader] >= 5:
                    continue
                open_by_book[book] += 1
                open_by_reader[reader] += 1
            staff = rng.choice(staff_ids)
            db.execute('INSERT INTO loans(book_id,reader_id,created_by,borrowed_on,due_on,returned_on,returned_by,extensions) VALUES(?,?,?,?,?,?,?,?)',
                       (book, reader, staff, borrowed.isoformat(), due.isoformat(),
                        returned.isoformat() if returned else None, rng.choice(staff_ids) if returned else None, extensions))
            if extensions:
                stats['extended'] += 1
            if returned:
                stats['returned'] += 1
                if returned > due:
                    stats['late_returned'] += 1
            elif due < today:
                stats['overdue'] += 1
            else:
                stats['open'] += 1

        counts = {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('users', 'books', 'readers', 'loans')}
    return counts, stats



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--demo', action='store_true', help='tạo CSDL demo lớn thay vì dữ liệu mẫu nhỏ')
    parser.add_argument('--db', default=None, help='đường dẫn CSDL demo (mặc định data/demo.db)')
    parser.add_argument('--force', action='store_true', help='xóa CSDL demo cũ nếu đã tồn tại')
    parser.add_argument('--seed', type=int, default=2026, help='hạt giống ngẫu nhiên cho demo')
    args = parser.parse_args(argv)
    if not args.demo:
        seed()
        return 0
    db_path = Path(args.db or ROOT / 'data/demo.db')
    if db_path.exists():
        if not args.force:
            print(f'{db_path} đã tồn tại; thêm --force để tạo lại.', file=sys.stderr)
            return 1
        db_path.unlink()
    counts, stats = seed_demo(db_path, date.today(), args.seed)
    print(f"Đã tạo {db_path}: {counts['users']} tài khoản, {counts['books']} đầu sách, {counts['readers']} độc giả, {counts['loans']} phiếu "
          f"({stats['open']} đang mượn trong hạn, {stats['overdue']} quá hạn, {stats['returned']} đã trả trong đó {stats['late_returned']} trả muộn, "
          f"{stats['extended']} đã gia hạn). Dữ liệu hư cấu.")
    print(f'Chạy: LIBRARY_DB={db_path} python -m uvicorn app.main:app --port 8001')
    return 0


if __name__ == '__main__':
    sys.exit(main())
