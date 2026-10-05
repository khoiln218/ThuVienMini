import os
import shutil
import sqlite3
import time
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parent.parent

def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    # Tìm kiếm không phân biệt hoa/thường Unicode ngay trong SQL (lower() của SQLite chỉ xử lý ASCII)
    db.create_function('casefold', 1, str.casefold, deterministic=True)
    return db

@contextmanager
def transaction():
    db = connect()
    try:
        db.execute('BEGIN IMMEDIATE')
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Cột bổ sung sau bản đầu; CREATE TABLE IF NOT EXISTS không thêm cột vào DB cũ nên phải ALTER.
MIGRATIONS = [
    ('users', 'active', 'INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))'),
    ('users', 'full_name', "TEXT NOT NULL DEFAULT ''"),
    ('users', 'email', "TEXT NOT NULL DEFAULT ''"),
    ('users', 'phone', "TEXT NOT NULL DEFAULT ''"),
    ('books', 'barcode', "TEXT NOT NULL DEFAULT ''"),
]
# Chỉ mục trên cột bổ sung và trên loans/loan_items: phải tạo sau ALTER/chuyển đổi nên không đặt trong schema.sql
POST_MIGRATION_SQL = [
    # Mã vạch duy nhất khi có nhập (chuỗi rỗng = chưa có, được phép trùng)
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_books_barcode ON books(barcode) WHERE barcode<>''",
    'CREATE INDEX IF NOT EXISTS ix_loans_reader ON loans(reader_id)',
    'CREATE INDEX IF NOT EXISTS ix_loans_due ON loans(due_on)',
    'CREATE INDEX IF NOT EXISTS ix_loan_items_book ON loan_items(book_id,returned_on)',
    'CREATE INDEX IF NOT EXISTS ix_loan_items_loan ON loan_items(loan_id,returned_on)',
]

def columns(db, table):
    return [row['name'] for row in db.execute(f'PRAGMA table_info({table})')]

def initialize():
    db = connect()
    try:
        # Bản cũ: mỗi dòng loans là một bản sách (có book_id, returned_on). Đổi tên để schema.sql tạo bảng loans mới
        # (phiếu) và loan_items (chi tiết); dữ liệu được chép sang trong giao dịch bên dưới.
        if 'book_id' in columns(db, 'loans'):
            db.execute('ALTER TABLE loans RENAME TO loans_v1')
            db.commit()
    finally:
        db.close()
    with transaction() as db:
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        for table, column, definition in MIGRATIONS:
            if column not in columns(db, table):
                db.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
        if columns(db, 'loans_v1'):
            extensions = 'extensions' if 'extensions' in columns(db, 'loans_v1') else '0'
            db.execute('INSERT INTO loans(id,reader_id,created_by,borrowed_on,due_on,extensions) '
                       f'SELECT id,reader_id,created_by,borrowed_on,due_on,{extensions} FROM loans_v1')
            db.execute('INSERT INTO loan_items(loan_id,book_id,returned_on,returned_by) '
                       'SELECT id,book_id,returned_on,returned_by FROM loans_v1 ORDER BY id')
            db.execute('DROP TABLE loans_v1')
        for sql in POST_MIGRATION_SQL:
            db.execute(sql)

def db_path():
    if os.environ.get('LIBRARY_DB'):
        return Path(os.environ['LIBRARY_DB'])
    if os.environ.get('VERCEL'):
        # Serverless (Vercel đặt sẵn VERCEL=1): mã nguồn nằm trên đĩa chỉ đọc, chỉ /tmp ghi được và mất khi
        # function khởi động lạnh. Chép CSDL mẫu ra /tmp một lần cho instance này → chế độ demo, không lưu bền.
        tmp = Path(os.environ.get('LIBRARY_TMP', '/tmp/thuvienmini')) / 'library.db'
        if not tmp.exists():
            tmp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / 'data/library.db', tmp)
        return tmp
    return ROOT / 'data/library.db'

def backup(keep=10):
    """Sao chép CSDL bằng API backup của SQLite (an toàn khi server đang chạy); giữ lại `keep` bản mới nhất."""
    source = db_path()
    folder = source.parent / 'backups'
    folder.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    target = folder / f'{source.stem}-{stamp}.db'
    for n in range(2, 100):  # tránh ghi đè nếu hai lần sao lưu trong cùng một giây
        if not target.exists(): break
        target = folder / f'{source.stem}-{stamp}-{n}.db'
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    for old in sorted(folder.glob(f'{source.stem}-*.db'))[:-keep]:
        old.unlink()
    return target

def query(sql, params=()):
    db = connect()
    try:
        return [dict(row) for row in db.execute(sql, params)]
    finally:
        db.close()
