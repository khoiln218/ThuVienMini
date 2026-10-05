// @ts-check
// Điểm vào của giao diện: đăng nhập/đăng xuất, gắn sự kiện chung, khởi động router.
import { api } from './api.js';
import { $, notice, showLogin } from './dom.js';
import { state, setPageSize, isAdmin } from './state.js';
import { navigate, routeFromPath } from './router.js';
import { refresh, mount } from './pages/index.js';
import { editBook } from './pages/books.js';
import { editReader } from './pages/readers.js';
import { newLoan, extendLoan, returnLoan, printLoan } from './pages/loans.js';
import { editUser, changePassword } from './pages/users.js';

/** @typedef {import('./types.js').User} User */

/** Báo lỗi ra dòng thông báo; dùng cho các hành động không nằm trong hộp thoại. @param {unknown} e */
const report = (e) => notice(/** @type {Error} */ (e).message, true);

/** Sau khi có phiên: hiện ứng dụng, điền tên người dùng, mở trang theo URL hiện tại. */
async function enter() {
  /** @type {User} */
  const user = await api('/me');
  state.user = user;
  $('#login-view').hidden = true;
  $('#app-view').hidden = false;
  $('#user-label').textContent =
    `${user.full_name || user.username} · ${user.role === 'admin' ? 'Quản trị viên' : 'Thủ thư'}`;
  // Phần tử chỉ dành cho quản trị (menu Tài khoản, nút Sao lưu...) đánh dấu bằng data-admin
  document.querySelectorAll('[data-admin]').forEach((el) => {
    /** @type {HTMLElement} */ (el).hidden = !isAdmin();
  });
  $('#today').textContent = new Date().toLocaleDateString('vi-VN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
  const route = routeFromPath();
  await navigate(route.page, route.param, true);
}

// Tải khung HTML các trang và dựng menu trước, rồi mới gắn sự kiện cho các nút bên trong (top-level await của ES module)
await mount();

// ---- Đăng nhập / đăng xuất ----
const loginForm = /** @type {HTMLFormElement} */ ($('#login-form'));
loginForm.onsubmit = async (e) => {
  e.preventDefault();
  const button = /** @type {HTMLButtonElement} */ (e.submitter);
  button.disabled = true;
  $('#login-error').textContent = '';
  try {
    await api('/login', 'POST', Object.fromEntries(new FormData(loginForm)));
    loginForm.reset();
    await enter();
  } catch (err) {
    $('#login-error').textContent = /** @type {Error} */ (err).message;
  } finally {
    button.disabled = false;
  }
};
$('#logout').onclick = async () => {
  try {
    await api('/logout', 'POST');
    state.user = null;
    showLogin();
  } catch (e) {
    report(e);
  }
};

// ---- Nút cố định trên trang ----
$('#add-book').onclick = () => editBook();
$('#add-reader').onclick = () => editReader();
$('#add-user').onclick = () => editUser();
$('#change-password').onclick = () => changePassword();
for (const id of ['#quick-borrow', '#add-loan']) $(id).onclick = () => newLoan().catch(report);
for (const id of ['#close-editor', '#cancel-editor'])
  $(id).onclick = () => /** @type {HTMLDialogElement} */ ($('#editor')).close();
$('#backup').onclick = async () => {
  try {
    const r = await api('/backup', 'POST');
    notice(`${r.message} · ${r.file}`);
  } catch (e) {
    report(e);
  }
};

// ---- Tìm kiếm, bộ lọc: quay về trang 1 ----
$('#book-search').onsubmit = (e) => {
  e.preventDefault();
  state.pageNo.books = 1;
  refresh().catch(report);
};
$('#reader-search').onsubmit = (e) => {
  e.preventDefault();
  state.pageNo.readers = 1;
  refresh().catch(report);
};
$('#loan-status').onchange = () => {
  state.pageNo.loans = 1;
  navigate('loans', undefined, true).catch(report);
};

// ---- Sự kiện ủy quyền cho các nút sinh động trong bảng (data-*) ----
document.addEventListener('click', async (e) => {
  const button = /** @type {HTMLElement} */ (e.target).closest('button');
  if (!button) return;
  const d = button.dataset;
  try {
    if (d.page) await navigate(/** @type {import('./types.js').PageName} */ (d.page));
    if (d.pager) {
      state.pageNo[/** @type {'books' | 'readers' | 'loans'} */ (d.pager)] = Number(d.go);
      await refresh();
    }
    if (d.editBook) editBook(Number(d.editBook));
    if (d.editReader) editReader(Number(d.editReader));
    if (d.editUser) editUser(Number(d.editUser));
    if (d.extend) extendLoan(Number(d.extend));
    if (
      d.toggleUser &&
      confirm(d.active === '1' ? 'Kích hoạt lại tài khoản này?' : 'Ngừng tài khoản này? Người đó sẽ bị đăng xuất ngay.')
    ) {
      await api(`/users/${d.toggleUser}`, 'PUT', { active: d.active === '1' });
      await refresh();
      notice('Đã cập nhật tài khoản.');
    }
    if (d.remove && confirm('Lưu trữ bản ghi này? Bản ghi sẽ ẩn khỏi danh sách, lịch sử mượn trả vẫn được giữ.')) {
      const r = await api(`/${d.remove}`, 'DELETE');
      await refresh();
      notice(r.message + '.');
    }
    if (d.return) await returnLoan(Number(d.return));
    if (d.print) await printLoan(Number(d.print));
  } catch (err) {
    report(err);
  } finally {
    button.disabled = false;
  }
});

// Link nội bộ (data-link) chuyển màn hình không tải lại trang
document.addEventListener('click', (e) => {
  const link = /** @type {HTMLElement} */ (e.target).closest('a[data-link]');
  if (!link || !state.user) return;
  e.preventDefault();
  history.pushState(null, '', link.getAttribute('href'));
  const route = routeFromPath();
  navigate(route.page, route.param, true).catch(report);
});

// Chọn số dòng mỗi trang
document.addEventListener('change', (e) => {
  const select = /** @type {HTMLElement} */ (e.target).closest('select[data-size]');
  if (!(select instanceof HTMLSelectElement)) return;
  setPageSize(Number(select.value));
  state.pageNo[/** @type {'books' | 'readers' | 'loans'} */ (select.dataset.size)] = 1;
  refresh().catch(report);
});

// Hộp thoại lưu xong (dom.js phát sự kiện) → vẽ lại trang
document.addEventListener('data-changed', () => refresh().catch(report));

// Back/Forward của trình duyệt
window.addEventListener('popstate', () => {
  if (!state.user) return;
  const route = routeFromPath();
  navigate(route.page, route.param, true).catch(report);
});

enter().catch(showLogin);
