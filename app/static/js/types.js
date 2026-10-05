// @ts-check
// Kiểu dữ liệu của API (khớp app/models.py và các endpoint trong app/main.py). Chỉ dùng cho JSDoc/@ts-check, không có mã chạy.

/** @typedef {{ id: number, username: string, full_name: string, email?: string, phone?: string, role: 'admin' | 'librarian', active?: number }} User */
/** @typedef {{ id: number, code: string, barcode: string, title: string, author: string, category: string, total: number, available: number }} Book */
/** @typedef {{ id: number, code: string, name: string, phone: string }} Reader */
/**
 * Một cuốn sách trong phiếu mượn (dòng loan_items).
 * @typedef {object} LoanItem
 * @property {number} id
 * @property {number} book_id
 * @property {string} title
 * @property {string} book_code
 * @property {string} author
 * @property {string | null} returned_on
 * @property {number} overdue_days
 */
/**
 * Phiếu mượn: mỗi lần mượn một phiếu, gồm một hoặc nhiều cuốn (items) với hạn trả chung.
 * @typedef {object} Loan
 * @property {number} id
 * @property {string} name
 * @property {string} reader_code
 * @property {string} reader_phone
 * @property {string} staff
 * @property {string} staff_name
 * @property {string} borrowed_on
 * @property {string} due_on
 * @property {string | null} returned_on  Ngày trả cuốn cuối cùng; null khi còn cuốn chưa trả
 * @property {number} extensions
 * @property {number} overdue_days
 * @property {number} pending  Số cuốn chưa trả
 * @property {LoanItem[]} items
 * @property {'open' | 'overdue' | 'returned'} status
 */
/** @typedef {{ titles: number, copies: number, available: number, readers: number, borrowing: number, overdue: number, returned: number, top_books: { title: string, count: number }[] }} Stats */
/**
 * Kết quả phân trang của /api/books, /api/readers, /api/loans khi có tham số page.
 * @template T
 * @typedef {{ items: T[], total: number, page: number, size: number, pages: number }} Page
 */
/** @typedef {'dashboard' | 'books' | 'readers' | 'loans' | 'users'} PageName */

export {};
