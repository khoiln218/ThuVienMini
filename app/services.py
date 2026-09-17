from datetime import date, timedelta
from fastapi import HTTPException
from .db import transaction

def overdue_days(due_on, returned_on=None, today=None):
    end = date.fromisoformat(returned_on) if returned_on else (today or date.today())
    return max(0, (end - date.fromisoformat(due_on)).days)

class LoanService:
    @staticmethod
    def borrow(data, user_id):
        with transaction() as db:
            book = db.execute('SELECT * FROM books WHERE id=? AND active=1', (data.book_id,)).fetchone()
            reader = db.execute('SELECT * FROM readers WHERE id=? AND active=1', (data.reader_id,)).fetchone()
            if not book or not reader:
                raise HTTPException(404, 'Sách hoặc độc giả không tồn tại / đã ngừng hoạt động')
            outstanding = db.execute('SELECT COUNT(*) FROM loans WHERE reader_id=? AND returned_on IS NULL', (data.reader_id,)).fetchone()[0]
            if outstanding >= 5:
                raise HTTPException(409, 'Độc giả đã mượn tối đa 5 sách')
            used = db.execute('SELECT COUNT(*) FROM loans WHERE book_id=? AND returned_on IS NULL', (data.book_id,)).fetchone()[0]
            if used >= book['total']:
                raise HTTPException(409, 'Sách đã hết bản có thể mượn')
            today = date.today()
            cur = db.execute('INSERT INTO loans(book_id,reader_id,created_by,borrowed_on,due_on) VALUES(?,?,?,?,?)',
                (data.book_id, data.reader_id, user_id, today.isoformat(), (today + timedelta(days=data.days)).isoformat()))
            return {'id': cur.lastrowid, 'message': 'Đã lập phiếu mượn'}

    @staticmethod
    def return_book(loan_id, user_id):
        with transaction() as db:
            loan = db.execute('SELECT * FROM loans WHERE id=?', (loan_id,)).fetchone()
            if not loan:
                raise HTTPException(404, 'Không tìm thấy phiếu mượn')
            if loan['returned_on']:
                raise HTTPException(409, 'Phiếu này đã trả sách')
            today = date.today().isoformat()
            db.execute('UPDATE loans SET returned_on=?,returned_by=? WHERE id=?', (today, user_id, loan_id))
            return {'message': 'Đã ghi nhận trả sách', 'overdue_days': overdue_days(loan['due_on'], today)}

    @staticmethod
    def extend(loan_id, days):
        with transaction() as db:
            loan = db.execute('SELECT * FROM loans WHERE id=?', (loan_id,)).fetchone()
            if not loan:
                raise HTTPException(404, 'Không tìm thấy phiếu mượn')
            if loan['returned_on']:
                raise HTTPException(409, 'Phiếu này đã trả sách')
            if overdue_days(loan['due_on']):
                raise HTTPException(409, 'Phiếu đã quá hạn, cần trả sách trước khi mượn lại')
            if loan['extensions'] >= 1:
                raise HTTPException(409, 'Mỗi phiếu chỉ được gia hạn một lần')
            new_due = (date.fromisoformat(loan['due_on']) + timedelta(days=days)).isoformat()
            db.execute('UPDATE loans SET due_on=?,extensions=extensions+1 WHERE id=?', (new_due, loan_id))
            return {'message': 'Đã gia hạn', 'due_on': new_due}
