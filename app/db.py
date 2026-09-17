import os
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
    ('loans', 'extensions', 'INTEGER NOT NULL DEFAULT 0 CHECK(extensions BETWEEN 0 AND 1)'),
    ('books', 'barcode', "TEXT NOT NULL DEFAULT ''"),
]
# Chỉ mục trên cột bổ sung: phải tạo sau ALTER nên không đặt trong schema.sql
POST_MIGRATION_SQL = [
    # Mã vạch duy nhất khi có nhập (chuỗi rỗng = chưa có, được phép trùng)
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_books_barcode ON books(barcode) WHERE barcode<>''",
]

def initialize():
    with transaction() as db:
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        for table, column, definition in MIGRATIONS:
            columns = [row['name'] for row in db.execute(f'PRAGMA table_info({table})')]
            if column not in columns:
                db.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
        for sql in POST_MIGRATION_SQL:
            db.execute(sql)

def db_path():
    return Path(os.environ.get('LIBRARY_DB', ROOT / 'data/library.db'))

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
