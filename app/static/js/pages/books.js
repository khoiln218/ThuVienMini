// @ts-check
import { api } from '../api.js';
import { $, html, empty, field, editor, toHTML } from '../dom.js';
import { state, isAdmin } from '../state.js';
import { pager } from './pager.js';

/** Thông tin để dựng menu và tiêu đề trang. */
export const meta = { title: 'Kho sách', label: 'Kho sách' };

/** @typedef {import('../types.js').Book} Book */

export async function render() {
  const q = /** @type {HTMLInputElement} */ ($('#book-search input')).value;
  /** @type {import('../types.js').Page<Book>} */
  const result = await api(`/books?q=${encodeURIComponent(q)}&page=${state.pageNo.books}&size=${state.pageSize}`);
  state.books = result.items;
  pager('books', result);

  $('#book-rows').innerHTML = toHTML(
    result.items.length
      ? result.items.map(
          (b) => html`
            <tr>
              <td>${b.code}</td>
              <td class="text-wrap"><b>${b.title}</b><small>${b.author}</small></td>
              <td>${b.category}</td>
              <td>${b.total}</td>
              <td><span class="badge ${b.available ? '' : 'late'}">${b.available}</span></td>
              <td>
                <button class="action" data-edit-book="${b.id}">Sửa</button>
                ${isAdmin() ? html`<button class="action danger" data-remove="books/${b.id}">Ngừng</button>` : ''}
              </td>
            </tr>
          `,
        )
      : empty(6, 'Không tìm thấy sách.'),
  );
}

/**
 * Hộp thoại thêm (không id) hoặc sửa sách.
 * @param {number} [id]
 */
export function editBook(id) {
  const b = state.books.find((x) => x.id === id);
  editor(
    id ? 'Chỉnh sửa sách' : 'Thêm sách mới',
    html`
      ${field('Mã sách', 'code', b?.code, 'required maxlength="30"')}
      ${field('Tên sách', 'title', b?.title, 'required maxlength="200"')}
      ${field('Tác giả', 'author', b?.author, 'required maxlength="100"')}
      ${field('Thể loại', 'category', b?.category, 'required maxlength="60"')}
      ${field('Tổng số bản', 'total', b?.total ?? 1, 'type="number" min="0" max="999" step="1" required')}
    `,
    (data) => api(id ? `/books/${id}` : '/books', id ? 'PUT' : 'POST', { ...data, total: Number(data.total) }),
  );
}
