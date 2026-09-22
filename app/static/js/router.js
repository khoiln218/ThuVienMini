// @ts-check
// Định tuyến phía client bằng History API: /, /books, /readers, /loans, /loans/overdue, /users.
// Server (app/main.py) trả index.html cho các đường dẫn này nên tải lại trang hoặc Back/Forward vẫn giữ đúng màn hình.
import { $ } from './dom.js';
import { state, isAdmin } from './state.js';
import { refresh, ROUTES } from './pages/index.js';
import { statusSelect } from './pages/loans.js';

/** @typedef {import('./types.js').PageName} PageName */

/** @param {string} name @returns {name is PageName} */
const isPage = (name) => Object.hasOwn(ROUTES, name);

/**
 * Đọc location.pathname thành {page, param}. Đường dẫn lạ hoặc trang không đủ quyền → tổng quan.
 * @returns {{ page: PageName, param?: string }}
 */
export function routeFromPath() {
  const [name = 'dashboard', param] = location.pathname.replace(/^\/+|\/+$/g, '').split('/');
  if (!isPage(name)) return { page: 'dashboard' };
  if (name === 'users' && !isAdmin()) return { page: 'dashboard' };
  return { page: name, param };
}

/**
 * Mở một trang: cập nhật URL, tiêu đề, menu, rồi tải dữ liệu.
 * @param {PageName} next
 * @param {string} [param]   Với trang loans: bộ lọc trạng thái (open/overdue/returned/all)
 * @param {boolean} [replace] true = replaceState (không tạo mục lịch sử mới), dùng khi khôi phục từ URL hoặc đổi bộ lọc
 */
export async function navigate(next, param, replace = false) {
  state.page = next;
  const select = statusSelect();
  if (next === 'loans' && param && [...select.options].some((o) => o.value === param)) {
    select.value = param;
    state.pageNo.loans = 1;
  }
  const filter = next === 'loans' && select.value !== 'all' ? `/${select.value}` : '';
  const path = next === 'dashboard' ? '/' : `/${next}${filter}`;
  if (location.pathname !== path) history[replace ? 'replaceState' : 'pushState'](null, '', path);

  document.title = `${ROUTES[next]} · Thư viện`;
  document.querySelectorAll('.page').forEach((el) => {
    /** @type {HTMLElement} */ (el).hidden = el.id !== next;
  });
  document.querySelectorAll('nav button').forEach((el) => {
    el.classList.toggle('active', /** @type {HTMLElement} */ (el).dataset.page === next);
  });
  $('#page-title').textContent = ROUTES[next];
  await refresh();
}
