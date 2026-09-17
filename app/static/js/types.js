// @ts-check
// Kiểu dữ liệu của API (khớp app/models.py và các endpoint trong app/main.py). Chỉ dùng cho JSDoc/@ts-check, không có mã chạy.

/** @typedef {{ id: number, username: string, role: 'admin' | 'librarian', active?: number }} User */
/** @typedef {{ id: number, code: string, title: string, author: string, category: string, total: number, available: number }} Book */
/** @typedef {{ id: number, code: string, name: string, phone: string }} Reader */
/**
 * @typedef {object} Loan
 * @property {number} id
 * @property {string} title
 * @property {string} book_code
 * @property {string} name
 * @property {string} reader_code
 * @property {string} borrowed_on
 * @property {string} due_on
 * @property {string | null} returned_on
 * @property {number} extensions
 * @property {number} overdue_days
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
