// @ts-check
import { showLogin } from './dom.js';

/**
 * Gọi API JSON. Luôn gửi header X-Library-Request (chống CSRF, xem current_user trong app/main.py).
 * Lỗi HTTP được ném ra dưới dạng Error với thông điệp tiếng Việt từ server; 401 thì quay về màn hình đăng nhập.
 * @param {string} path  Đường dẫn sau /api, ví dụ '/books?page=1'
 * @param {'GET' | 'POST' | 'PUT' | 'DELETE'} [method]
 * @param {unknown} [body]
 * @returns {Promise<any>}  Người gọi tự ghi kiểu kết quả bằng JSDoc (xem types.js)
 */
export async function api(path, method = 'GET', body) {
  const response = await fetch('/api' + path, {
    method,
    headers: { 'Content-Type': 'application/json', 'X-Library-Request': '1' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401 && path !== '/login') showLogin();
    const detail = data.detail;
    // Lỗi kiểm tra dữ liệu của FastAPI là mảng {loc, msg}; gom thành từng dòng "trường: lý do"
    const message = Array.isArray(detail)
      ? detail.map((e) => e.loc.slice(1).join('.') + ': ' + e.msg).join('\n')
      : detail || 'Không thể thực hiện yêu cầu';
    throw new Error(message);
  }
  return data;
}
