from datetime import date, timedelta
from fastapi import HTTPException
from .db import transaction
from .models import MAX_BORROWED

def overdue_days(due_on, returned_on=None, today=None):
    end = date.fromisoformat(returned_on) if returned_on else (today or date.today())
    return max(0, (end - date.fromisoformat(due_on)).days)

def open_items(db, loan_id):
    return db.execute('SELECT * FROM loan_items WHERE loan_id=? AND returned_on IS NULL ORDER BY id', (loan_id,)).fetchall()

class LoanService:
    @staticmethod
    def borrow(data, user_id):
        """Mỗi lần mượn lập một phiếu (loans) kèm một dòng chi tiết (loan_items) cho mỗi bản sách."""
        if len(set(data.book_ids)) != len(data.book_ids):
            raise HTTPException(422, 'Mỗi đầu sách chỉ được chọn một lần trong phiếu')
        with transaction() as db:
            reader = db.execute('SELECT * FROM readers WHERE id=? AND active=1', (data.reader_id,)).fetchone()
            if not reader:
                raise HTTPException(404, 'Độc giả không tồn tại hoặc đã được lưu trữ')
            books = []
            for book_id in data.book_ids:
                book = db.execute('SELECT * FROM books WHERE id=? AND active=1', (book_id,)).fetchone()
                if not book:
                    raise HTTPException(404, 'Sách không tồn tại hoặc đã được lưu trữ')
                books.append(book)
            holding = db.execute('SELECT COUNT(*) FROM loan_items i JOIN loans l ON l.id=i.loan_id '
                                 'WHERE l.reader_id=? AND i.returned_on IS NULL', (data.reader_id,)).fetchone()[0]
            if holding + len(books) > MAX_BORROWED:
                raise HTTPException(409, f'Độc giả đang giữ {holding} cuốn, chỉ được mượn thêm {max(0, MAX_BORROWED - holding)} cuốn')
            for book in books:
                used = db.execute('SELECT COUNT(*) FROM loan_items WHERE book_id=? AND returned_on IS NULL', (book['id'],)).fetchone()[0]
                if used >= book['total']:
                    raise HTTPException(409, f'Sách "{book["title"]}" đã hết bản có thể mượn')
            today = date.today()
            cur = db.execute('INSERT INTO loans(reader_id,created_by,borrowed_on,due_on) VALUES(?,?,?,?)',
                (data.reader_id, user_id, today.isoformat(), (today + timedelta(days=data.days)).isoformat()))
            db.executemany('INSERT INTO loan_items(loan_id,book_id) VALUES(?,?)', [(cur.lastrowid, b['id']) for b in books])
            return {'id': cur.lastrowid, 'message': f'Đã lập phiếu mượn #{cur.lastrowid} gồm {len(books)} cuốn'}

    @staticmethod
    def return_books(loan_id, item_ids, user_id):
        """Nhận trả các cuốn được chọn của phiếu; không chọn thì nhận trả toàn bộ sách còn lại."""
        with transaction() as db:
            loan = db.execute('SELECT * FROM loans WHERE id=?', (loan_id,)).fetchone()
            if not loan:
                raise HTTPException(404, 'Không tìm thấy phiếu mượn')
            pending = {row['id'] for row in open_items(db, loan_id)}
            if not pending:
                raise HTTPException(409, 'Phiếu này đã trả hết sách')
            chosen = set(item_ids) if item_ids else pending
            if chosen - pending:
                raise HTTPException(409, 'Có cuốn đã trả hoặc không thuộc phiếu này')
            today = date.today().isoformat()
            db.executemany('UPDATE loan_items SET returned_on=?,returned_by=? WHERE id=?', [(today, user_id, i) for i in chosen])
            remaining = len(pending) - len(chosen)
            message = f'Đã nhận trả {len(chosen)} cuốn của phiếu #{loan_id}'
            message += f', phiếu còn {remaining} cuốn chưa trả' if remaining else ', phiếu đã trả đủ'
            return {'message': message, 'returned': len(chosen), 'remaining': remaining,
                    'overdue_days': overdue_days(loan['due_on'], today)}

    @staticmethod
    def extend(loan_id, days):
        with transaction() as db:
            loan = db.execute('SELECT * FROM loans WHERE id=?', (loan_id,)).fetchone()
            if not loan:
                raise HTTPException(404, 'Không tìm thấy phiếu mượn')
            if not open_items(db, loan_id):
                raise HTTPException(409, 'Phiếu này đã trả hết sách')
            if overdue_days(loan['due_on']):
                raise HTTPException(409, 'Phiếu đã quá hạn, cần trả sách trước khi mượn lại')
            if loan['extensions'] >= 1:
                raise HTTPException(409, 'Mỗi phiếu chỉ được gia hạn một lần')
            new_due = (date.fromisoformat(loan['due_on']) + timedelta(days=days)).isoformat()
            db.execute('UPDATE loans SET due_on=?,extensions=extensions+1 WHERE id=?', (new_due, loan_id))
            return {'message': f'Đã gia hạn phiếu #{loan_id} đến {new_due}', 'due_on': new_due}
