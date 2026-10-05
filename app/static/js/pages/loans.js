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
              <td><b>#${l.id}</b><small>Lập bởi ${l.staff}</small></td>
              <td class="text-wrap">
                <ul class="loan-books">
                  ${l.items.map(
                    (i) =>
                      html`<li class="${i.returned_on ? 'returned' : ''}">
                        ${i.title}<small>${i.book_code}${i.returned_on ? html` · đã trả ${i.returned_on}` : ''}</small>
                      </li>`,
                  )}
                </ul>
              </td>
              <td>${l.name}<small>${l.reader_code}</small></td>
              <td>${l.borrowed_on}</td>
              <td>${l.due_on}${l.extensions ? html`<small>Đã gia hạn</small>` : ''}</td>
              <td>${badge(l)}</td>
              <td>
                ${
                  l.returned_on
                    ? html`<small>Trả xong: ${l.returned_on}</small>`
                    : html`
                        <button class="action" data-return="${l.id}">Trả sách</button>
                        ${l.status === 'open' && !l.extensions ? html`<button class="action" data-extend="${l.id}">Gia hạn</button>` : ''}
                      `
                }
              </td>
            </tr>
          `,
        )
      : empty(7),
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
    'Gia hạn',
  );
}

/** Giá trị các ô đánh dấu đang chọn trong hộp thoại (FormData gộp về một giá trị nên phải đọc trực tiếp). @param {string} name */
const checked = (name) =>
  [...document.querySelectorAll(`#editor input[name="${name}"]:checked`)].map((el) =>
    Number(/** @type {HTMLInputElement} */ (el).value),
  );

/** Hộp thoại nhận trả sách: chọn những cuốn độc giả mang trả (mặc định cả phiếu). @param {number} id */
export async function returnLoan(id) {
  /** @type {Loan} */
  const loan = await api(`/loans/${id}`);
  const pending = loan.items.filter((i) => !i.returned_on);
  editor(
    `Nhận trả sách · phiếu #${id}`,
    html`
      <p>
        Độc giả <b>${loan.name}</b> (${loan.reader_code}) · hạn trả ${loan.due_on}
        ${loan.overdue_days ? html`<span class="badge late">Quá hạn ${loan.overdue_days} ngày</span>` : ''}
      </p>
      <fieldset class="checklist">
        <legend>Chọn sách đã nhận lại</legend>
        ${pending.map(
          (i) =>
            html`<label
              ><input type="checkbox" name="item" value="${i.id}" checked />${i.title}<small
                >${i.book_code}</small
              ></label
            >`,
        )}
      </fieldset>
      <p class="hint">Bỏ chọn những cuốn độc giả chưa mang trả; phiếu vẫn mở cho tới khi trả đủ.</p>
    `,
    () => {
      const items = checked('item');
      if (!items.length) throw new Error('Chọn ít nhất một cuốn sách');
      return api(`/loans/${id}/return`, 'POST', { item_ids: items });
    },
    'Xác nhận đã nhận sách',
  );
}

/** Hộp thoại lập phiếu mượn: một độc giả, một hoặc nhiều đầu sách còn bản (mỗi đầu sách một bản). */
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
      <fieldset class="checklist">
        <legend>Sách mượn <span id="picked">(đã chọn 0)</span></legend>
        <input type="search" id="book-filter" placeholder="Lọc theo mã hoặc tên sách…" aria-label="Lọc sách" />
        <div class="checklist-scroll">
          ${available.map(
            (b) =>
              html`<label data-text="${(b.code + ' ' + b.title).toLowerCase()}"
                ><input type="checkbox" name="book" value="${b.id}" />${b.title}<small
                  >${b.code} · còn ${b.available}</small
                ></label
              >`,
          )}
        </div>
      </fieldset>
      ${field('Số ngày mượn', 'days', 14, 'type="number" min="1" max="30" step="1" required')}
      <p class="hint">
        Mỗi lần mượn lập một phiếu, tối đa 5 cuốn; mỗi độc giả giữ tối đa 5 cuốn cùng lúc. Hạn trả tính từ hôm nay.
      </p>
    `,
    (data) => {
      const bookIds = checked('book');
      if (!bookIds.length) throw new Error('Chọn ít nhất một cuốn sách');
      return api('/loans', 'POST', { reader_id: Number(data.reader_id), book_ids: bookIds, days: Number(data.days) });
    },
    'Lập phiếu',
  );
  const filter = /** @type {HTMLInputElement} */ ($('#book-filter'));
  filter.oninput = () => {
    const q = filter.value.trim().toLowerCase();
    /** @type {NodeListOf<HTMLElement>} */
    const labels = document.querySelectorAll('#editor .checklist-scroll label');
    labels.forEach((el) => {
      el.hidden = !(el.dataset.text ?? '').includes(q);
    });
  };
  // Enter trong ô lọc không được gửi biểu mẫu
  filter.onkeydown = (e) => {
    if (e.key === 'Enter') e.preventDefault();
  };
  $('#editor-fields').onchange = () => {
    $('#picked').textContent = `(đã chọn ${checked('book').length})`;
  };
}
