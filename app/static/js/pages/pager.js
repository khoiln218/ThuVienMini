// @ts-check
import { $, html, raw, toHTML } from '../dom.js';
import { state } from '../state.js';

const SIZES = [5, 10, 20, 50];

/**
 * Vẽ thanh phân trang dưới một bảng: số bản ghi, trang x/y, chọn số dòng, nút Trước/Sau.
 * Các nút mang data-pager/data-go và select mang data-size; main.js bắt sự kiện chung.
 * @param {'books' | 'readers' | 'loans'} key
 * @param {import('../types.js').Page<unknown>} result
 */
export function pager(key, result) {
  const el = $(`#${key}-pager`);
  el.hidden = false;
  el.innerHTML = toHTML(html`
    <span>${result.total} bản ghi · Trang ${result.page}/${result.pages}</span>
    <span>
      <label class="filter">
        Hiển thị
        <select data-size="${key}">
          ${SIZES.map((n) => html`<option value="${n}" ${n === state.pageSize ? raw('selected') : ''}>${n} dòng</option>`)}
        </select>
      </label>
      <button data-pager="${key}" data-go="${result.page - 1}" ${result.page <= 1 ? raw('disabled') : ''}>
        ← Trước
      </button>
      <button data-pager="${key}" data-go="${result.page + 1}" ${result.page >= result.pages ? raw('disabled') : ''}>
        Sau →
      </button>
    </span>
  `);
  state.pageNo[key] = result.page;
}
