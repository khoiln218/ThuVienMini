// @ts-check
import { api } from '../api.js';
import { $, html, raw, empty, field, editor, toHTML } from '../dom.js';
import { state } from '../state.js';

/** Thông tin để dựng menu và tiêu đề trang. */
export const meta = { title: 'Tài khoản nhân viên', label: 'Tài khoản', adminOnly: true };

/** @typedef {import('../types.js').User} User */

const ROLE_LABEL = { admin: 'Quản trị viên', librarian: 'Thủ thư' };

export async function render() {
  /** @type {User[]} */
  const users = await api('/users');
  state.users = users;
  const me = state.user?.id;

  $('#user-rows').innerHTML = toHTML(
    users.length
      ? users.map(
          (u) => html`
            <tr>
              <td><b>${u.username}</b>${u.id === me ? html`<small>Bạn</small>` : ''}</td>
              <td>${u.full_name || '—'}</td>
              <td>${u.email || '—'}<small>${u.phone}</small></td>
              <td>${ROLE_LABEL[u.role]}</td>
              <td><span class="badge ${u.active ? 'done' : 'late'}">${u.active ? 'Hoạt động' : 'Đã ngừng'}</span></td>
              <td>
                <button class="action" data-edit-user="${u.id}">Sửa</button>
                ${
                  u.id === me
                    ? ''
                    : html`<button
                        class="action ${u.active ? 'danger' : ''}"
                        data-toggle-user="${u.id}"
                        data-active="${u.active ? 0 : 1}"
                      >
                        ${u.active ? 'Ngừng' : 'Kích hoạt'}
                      </button>`
                }
              </td>
            </tr>
          `,
        )
      : empty(6),
  );
}

/** @param {string | undefined} value */
const roleSelect = (value) => html`
  <label>
    Vai trò
    <select name="role">
      <option value="librarian" ${value !== 'admin' ? raw('selected') : ''}>Thủ thư</option>
      <option value="admin" ${value === 'admin' ? raw('selected') : ''}>Quản trị viên</option>
    </select>
  </label>
`;

/**
 * Hộp thoại thêm tài khoản (không id) hoặc sửa vai trò / đặt lại mật khẩu (có id). Chỉ admin thấy trang này.
 * @param {number} [id]
 */
export function editUser(id) {
  const u = state.users.find((x) => x.id === id);
  editor(
    id ? `Chỉnh sửa tài khoản ${u?.username ?? ''}` : 'Thêm tài khoản',
    html`
      ${id ? '' : field('Tên đăng nhập', 'username', '', 'required minlength="3" maxlength="50" pattern="[A-Za-z0-9._-]+" autocomplete="off"')}
      ${field('Họ và tên', 'full_name', u?.full_name, 'required maxlength="100"')}
      ${field('Email (không bắt buộc)', 'email', u?.email, 'type="email" maxlength="100"')}
      ${field('Điện thoại (không bắt buộc)', 'phone', u?.phone, 'maxlength="20" inputmode="tel"')}
      ${roleSelect(u?.role)}
      ${field(
        id ? 'Mật khẩu mới (để trống nếu không đổi)' : 'Mật khẩu',
        'password',
        '',
        `${id ? '' : 'required '}type="password" minlength="8" maxlength="128" autocomplete="new-password"`,
      )}
      <p class="hint">Mật khẩu tối thiểu 8 ký tự. Đặt lại mật khẩu sẽ đăng xuất tài khoản đó khỏi mọi phiên.</p>
    `,
    (data) => {
      if (!id) return api('/users', 'POST', data);
      /** @type {{ role: string, full_name: string, email: string, phone: string, password?: string }} */
      const body = { role: data.role, full_name: data.full_name, email: data.email, phone: data.phone };
      if (data.password) body.password = data.password;
      return api(`/users/${id}`, 'PUT', body);
    },
  );
}

/** Hộp thoại đổi mật khẩu của chính mình (mọi vai trò). */
export function changePassword() {
  editor(
    'Đổi mật khẩu',
    html`
      ${field('Mật khẩu hiện tại', 'current_password', '', 'type="password" required autocomplete="current-password"')}
      ${field('Mật khẩu mới', 'new_password', '', 'type="password" required minlength="8" maxlength="128" autocomplete="new-password"')}
      ${field('Nhập lại mật khẩu mới', 'confirm', '', 'type="password" required autocomplete="new-password"')}
    `,
    async (data) => {
      if (data.new_password !== data.confirm) throw new Error('Mật khẩu nhập lại không khớp');
      await api('/password', 'POST', { current_password: data.current_password, new_password: data.new_password });
    },
  );
}
