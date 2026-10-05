CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','librarian')),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 full_name TEXT NOT NULL DEFAULT '', email TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT ''
);
-- Bảng sessions không còn dùng từ bản token ký HMAC (giữ lại để CSDL cũ không lỗi)
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS books (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
 author TEXT NOT NULL, category TEXT NOT NULL, total INTEGER NOT NULL CHECK(total BETWEEN 0 AND 999),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 barcode TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS readers (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
 phone TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
-- Phiếu mượn: mỗi lần mượn lập một phiếu, hạn trả và gia hạn tính chung cho cả phiếu
CREATE TABLE IF NOT EXISTS loans (
 id INTEGER PRIMARY KEY, reader_id INTEGER NOT NULL REFERENCES readers(id),
 created_by INTEGER NOT NULL REFERENCES users(id),
 borrowed_on TEXT NOT NULL, due_on TEXT NOT NULL,
 extensions INTEGER NOT NULL DEFAULT 0 CHECK(extensions BETWEEN 0 AND 1),
 CHECK(due_on >= borrowed_on)
);
-- Chi tiết phiếu mượn: mỗi dòng là một bản sách trong phiếu, trả riêng từng cuốn
CREATE TABLE IF NOT EXISTS loan_items (
 id INTEGER PRIMARY KEY, loan_id INTEGER NOT NULL REFERENCES loans(id),
 book_id INTEGER NOT NULL REFERENCES books(id),
 returned_on TEXT, returned_by INTEGER REFERENCES users(id),
 UNIQUE(loan_id, book_id)
);
-- Chỉ mục của loans/loan_items tạo trong app/db.py (POST_MIGRATION_SQL) sau khi chuyển CSDL cũ sang mô hình phiếu + chi tiết
