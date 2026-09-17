// @ts-check
import { api } from '../api.js';
import { $, html, empty, field, editor, toHTML } from '../dom.js';
import { state, isAdmin } from '../state.js';
import { pager } from './pager.js';

/** Thông tin để dựng menu và tiêu đề trang. */
export const meta = { title: 'Quản lý độc giả', label: 'Độc giả' };

/** @typedef {import('../types.js').Reader} Reader */

export async function render() {
  const q = /** @type {HTMLInputElement} */ ($('#reader-search input')).value;
  /** @type {import('../types.js').Page<Reader>} */
  const result = await api(`/readers?q=${encodeURIComponent(q)}&page=${state.pageNo.readers}&size=${state.pageSize}`);
  state.readers = result.items;
  pager('readers', result);

  $('#reader-rows').innerHTML = toHTML(
    result.items.length
      ? result.items.map(
          (r) => html`
            <tr>
              <td>${r.code}</td>
              <td>${r.name}</td>
              <td>${r.phone || '—'}</td>
              <td>
                <button class="action" data-edit-reader="${r.id}">Sửa</button>
                ${isAdmin() ? html`<button class="action danger" data-remove="readers/${r.id}">Ngừng</button>` : ''}
              </td>
            </tr>
          `,
        )
      : empty(4, 'Không tìm thấy độc giả.'),
  );
}

/**
 * Hộp thoại thêm (không id) hoặc sửa độc giả.
 * @param {number} [id]
 */
export function editReader(id) {
  const r = state.readers.find((x) => x.id === id);
  editor(
    id ? 'Chỉnh sửa độc giả' : 'Thêm độc giả',
    html`
      ${field('Mã độc giả', 'code', r?.code, 'required maxlength="30"')}
      ${field('Họ và tên', 'name', r?.name, 'required maxlength="100"')}
      ${field('Điện thoại (không bắt buộc)', 'phone', r?.phone, 'maxlength="20" type="tel"')}
    `,
    (data) => api(id ? `/readers/${id}` : '/readers', id ? 'PUT' : 'POST', data),
  );
}
