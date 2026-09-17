CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','librarian'))
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS books (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
 author TEXT NOT NULL, category TEXT NOT NULL, total INTEGER NOT NULL CHECK(total BETWEEN 0 AND 999),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS readers (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
 phone TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS loans (
 id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books(id),
 reader_id INTEGER NOT NULL REFERENCES readers(id), created_by INTEGER NOT NULL REFERENCES users(id),
 borrowed_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT,
 returned_by INTEGER REFERENCES users(id), CHECK(due_on >= borrowed_on),
 CHECK(returned_on IS NULL OR returned_on >= borrowed_on)
);
CREATE INDEX IF NOT EXISTS ix_loans_book ON loans(book_id,returned_on);
CREATE INDEX IF NOT EXISTS ix_loans_reader ON loans(reader_id,returned_on);
CREATE INDEX IF NOT EXISTS ix_loans_due ON loans(due_on) WHERE returned_on IS NULL;
