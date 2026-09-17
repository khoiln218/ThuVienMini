// @ts-check
/** @typedef {import('./types.js').User} User */
/** @typedef {import('./types.js').Book} Book */
/** @typedef {import('./types.js').Reader} Reader */
/** @typedef {import('./types.js').PageName} PageName */

/** @returns {number} */
function storedPageSize() {
  try {
    return Number(localStorage.getItem('pageSize')) || 20;
  } catch {
    return 20;
  }
}

/** Trạng thái dùng chung của giao diện. Các trang đọc/ghi qua đối tượng này thay vì biến toàn cục. */
export const state = {
  /** @type {User | null} */ user: null,
  /** @type {PageName} */ page: 'dashboard',
  /** Trang hiện tại của từng bảng */
  pageNo: { books: 1, readers: 1, loans: 1 },
  pageSize: storedPageSize(),
  // Dữ liệu đang hiển thị, để hộp thoại "Sửa" lấy bản ghi theo id mà không gọi lại API
  /** @type {Book[]} */ books: [],
  /** @type {Reader[]} */ readers: [],
  /** @type {User[]} */ users: [],
};

/** @param {number} size */
export function setPageSize(size) {
  state.pageSize = size;
  try {
    localStorage.setItem('pageSize', String(size));
  } catch {
    // Chế độ riêng tư hoặc bị chặn lưu trữ: bỏ qua, chỉ mất ghi nhớ giữa các lần mở
  }
}

export const isAdmin = () => state.user?.role === 'admin';
