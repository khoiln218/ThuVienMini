import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parent.parent

def connect():
    path = Path(os.environ.get('LIBRARY_DB', ROOT / 'data/library.db'))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
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

def initialize():
    with transaction() as db:
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))

def query(sql, params=()):
    db = connect()
    try:
        return [dict(row) for row in db.execute(sql, params)]
    finally:
        db.close()
