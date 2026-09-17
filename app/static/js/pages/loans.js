// @ts-check
import { api } from '../api.js';
import { $, html, empty, field, editor, notice, toHTML } from '../dom.js';
import { state } from '../state.js';
import { pager } from './pager.js';

/** Thông tin để dựng menu và tiêu đề trang. */
export const meta = { title: 'Mượn & trả sách', label: 'Mượn & trả' };

/** @typedef {import('../types.js').Loan} Loan */
/** @typedef {import('../types.js').Book} Book */
/** @typedef {import('../types.js').Reader} Reader */

/** Ô trạng thái phiếu: đang mượn / quá hạn n ngày / đã trả. @param {Loan} l */
export function badge(l) {
  const cls = l.status === 'overdue' ? 'late' : l.status === 'returned' ? 'done' : '';
  const text =
    l.status === 'returned' ? 'Đã trả' : l.status === 'overdue' ? `Quá hạn ${l.overdue_days} ngày` : 'Đang mượn';
  return html`<span class="badge ${cls}">${text}</span>`;
}

export const statusSelect = () => /** @type {HTMLSelectElement} */ ($('#loan-status'));

export async function render() {
  /** @type {import('../types.js').Page<Loan>} */
  const result = await api(`/loans?status=${statusSelect().value}&page=${state.pageNo.loans}&size=${state.pageSize}`);
  pager('loans', result);

  $('#loan-rows').innerHTML = toHTML(
    result.items.length
      ? result.items.map(
          (l) => html`
            <tr>
              <td class="text-wrap"><b>${l.title}</b><small>#${l.id} · ${l.book_code}</small></td>
              <td>${l.name}<small>${l.reader_code}</small></td>
              <td>${l.borrowed_on}</td>
              <td>${l.due_on}${l.extensions ? html`<small>Đã gia hạn</small>` : ''}</td>
              <td>${badge(l)}</td>
              <td>
                ${
                  l.returned_on
                    ? html`<small>Trả: ${l.returned_on}</small>`
                    : html`
                        <button class="action" data-return="${l.id}">Trả sách</button>
                        ${l.status === 'open' && !l.extensions ? html`<button class="action" data-extend="${l.id}">Gia hạn</button>` : ''}
                      `
                }
              </td>
            </tr>
          `,
        )
      : empty(6),
  );
}

/** Hộp thoại gia hạn một phiếu đang trong hạn. @param {number} id */
export function extendLoan(id) {
  editor(
    `Gia hạn phiếu #${id}`,
    html`
      ${field('Số ngày gia hạn thêm', 'days', 7, 'type="number" min="1" max="30" step="1" required')}
      <p class="hint">Tính từ hạn trả hiện tại. Mỗi phiếu chỉ gia hạn một lần và chỉ khi còn trong hạn.</p>
    `,
    (data) => api(`/loans/${id}/extend`, 'POST', { days: Number(data.days) }),
  );
}

/** Hộp thoại lập phiếu mượn: tải toàn bộ sách còn bản và độc giả hoạt động (không phân trang). */
export async function newLoan() {
  /** @type {[Book[], Reader[]]} */
  const [books, readers] = await Promise.all([api('/books'), api('/readers')]);
  const available = books.filter((b) => b.available > 0);
  if (!available.length || !readers.length) {
    notice('Cần có sách còn bản và độc giả hoạt động trước khi lập phiếu.', true);
    return;
  }
  editor(
    'Lập phiếu mượn',
    html`
      <label>
        Độc giả
        <select name="reader_id" required>
          ${readers.map((r) => html`<option value="${r.id}">${r.code} · ${r.name}</option>`)}
        </select>
      </label>
      <label>
        Sách
        <select name="book_id" required>
          ${available.map((b) => html`<option value="${b.id}">${b.code} · ${b.title} (còn ${b.available})</option>`)}
        </select>
      </label>
      ${field('Số ngày mượn', 'days', 14, 'type="number" min="1" max="30" step="1" required')}
      <p class="hint">
        Một phiếu = một bản sách. Mỗi độc giả được giữ tối đa 5 bản. Hạn trả được tính từ ngày hôm nay.
      </p>
    `,
    (data) =>
      api('/loans', 'POST', {
        book_id: Number(data.book_id),
        reader_id: Number(data.reader_id),
        days: Number(data.days),
      }),
  );
}
