// @ts-check
// Tiện ích DOM: chọn phần tử, tạo HTML an toàn, thông báo, hộp thoại chỉnh sửa.

/**
 * document.querySelector rút gọn. Trả về HTMLElement để dùng .hidden/.textContent không cần ép kiểu.
 * @param {string} selector
 * @returns {HTMLElement}
 */
export const $ = (selector) => /** @type {HTMLElement} */ (document.querySelector(selector));

/**
 * Thoát ký tự HTML. Mọi giá trị chèn vào template `html` đều đi qua đây.
 * @param {unknown} value
 */
export const esc = (value) =>
  String(value ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );

/** Đoạn HTML đã an toàn (kết quả của `html` hoặc `raw`). */
class Fragment {
  /** @param {string} source */
  constructor(source) {
    this.source = source;
  }
  toString() {
    return this.source;
  }
}

/**
 * Đánh dấu một chuỗi HTML là tin cậy (chỉ dùng cho hằng số trong mã, không dùng cho dữ liệu người dùng).
 * @param {string} source
 */
export const raw = (source) => new Fragment(source);

/** @param {unknown} value */
function stringify(value) {
  if (value instanceof Fragment) return value.source;
  if (Array.isArray(value)) return value.map(stringify).join('');
  if (value === null || value === undefined || value === false) return '';
  return esc(value);
}

/**
 * Tagged template tạo HTML: giá trị chèn vào được thoát tự động, trừ Fragment lồng nhau và mảng Fragment.
 *   el.innerHTML = html`<b>${book.title}</b>`;   // an toàn dù title chứa <script>
 * @param {TemplateStringsArray} strings
 * @param {...unknown} values
 */
export function html(strings, ...values) {
  let out = strings[0];
  values.forEach((value, i) => {
    out += stringify(value) + strings[i + 1];
  });
  return new Fragment(out);
}

/**
 * Chuyển một mảng Fragment (hoặc một Fragment) thành chuỗi HTML để gán vào innerHTML.
 * Không dùng String(mảng) vì Array.toString nối bằng dấu phẩy.
 * @param {unknown} content
 */
export const toHTML = (content) => stringify(content);

/**
 * Hiện dòng thông báo phía trên nội dung.
 * @param {string} message
 * @param {boolean} [error]
 */
export function notice(message, error = false) {
  const el = $('#notification');
  el.textContent = message;
  el.hidden = false;
  el.style.background = error ? '#fbe9e1' : '#e4eee3';
}

export function showLogin() {
  $('#app-view').hidden = true;
  $('#login-view').hidden = false;
  /** @type {HTMLDialogElement} */ ($('#editor')).close();
}

/**
 * Hàng trống cho bảng.
 * @param {number} cols
 * @param {string} [text]
 */
export const empty = (cols, text = 'Chưa có dữ liệu') =>
  html`<tr>
    <td colspan="${cols}" class="empty">${text}</td>
  </tr>`;

/**
 * Một ô nhập trong hộp thoại. `extra` là thuộc tính HTML tin cậy (required, maxlength...).
 * @param {string} label
 * @param {string} name
 * @param {string | number} [value]
 * @param {string} [extra]
 */
export const field = (label, name, value = '', extra = '') =>
  html`<label>${label}<input name="${name}" value="${value}" ${raw(extra)} /></label>`;

/**
 * Mở hộp thoại chỉnh sửa. `submitLabel` đổi chữ trên nút xác nhận (mặc định "Lưu thông tin"). Khi lưu thành công: đóng hộp thoại và phát sự kiện `data-changed` để trang tự tải lại.
 * @param {string} title
 * @param {Fragment} fields
 * @param {(data: Record<string, string>) => Promise<unknown>} save
 * @param {string} [submitLabel]
 */
export function editor(title, fields, save, submitLabel = 'Lưu thông tin') {
  const dialog = /** @type {HTMLDialogElement} */ ($('#editor'));
  const form = /** @type {HTMLFormElement} */ ($('#editor-form'));
  $('#editor-title').textContent = title;
  $('#editor-fields').innerHTML = String(fields);
  $('#editor-error').textContent = '';
  $('#editor-submit').textContent = submitLabel;
  form.onsubmit = async (event) => {
    event.preventDefault();
    const button = /** @type {HTMLButtonElement} */ (event.submitter);
    button.disabled = true;
    try {
      const result = await save(/** @type {Record<string, string>} */ (Object.fromEntries(new FormData(form))));
      dialog.close();
      document.dispatchEvent(new CustomEvent('data-changed'));
      // Hiển thị kết quả server trả về (ví dụ "Đã lập phiếu mượn #12 gồm 2 cuốn"), không có thì thông báo chung
      const message = /** @type {{ message?: unknown } | undefined} */ (result)?.message;
      notice(typeof message === 'string' ? message + '.' : 'Đã lưu thay đổi.');
    } catch (e) {
      $('#editor-error').textContent = /** @type {Error} */ (e).message;
    } finally {
      button.disabled = false;
    }
  };
  dialog.showModal();
}
