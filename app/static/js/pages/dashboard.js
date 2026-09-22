// @ts-check
import { api } from '../api.js';
import { $, html, toHTML } from '../dom.js';
import { badge } from './loans.js';

/** Thông tin để dựng menu và tiêu đề trang. */
export const meta = { title: 'Tổng quan thư viện', label: 'Tổng quan' };

/** @typedef {import('../types.js').Stats} Stats */
/** @typedef {import('../types.js').Loan} Loan */

export async function render() {
  /** @type {[Stats, Loan[]]} */
  const [stats, overdue] = await Promise.all([api('/stats'), api('/loans?status=overdue')]);

  const tiles = [
    ['Đầu sách', stats.titles, `${stats.copies} bản trong kho`],
    ['Bản có sẵn', stats.available, `${stats.readers} độc giả hoạt động`],
    ['Đang mượn', stats.borrowing, `${stats.returned} phiếu đã trả`],
    ['Phiếu quá hạn', stats.overdue, 'Cần theo dõi hoàn trả'],
  ];
  $('#stats').innerHTML = toHTML(
    tiles.map(
      ([label, value, sub], i) =>
        html`<div class="stat ${i === 3 ? 'alert' : ''}">
          <span>${label}</span><strong>${value}</strong><span>${sub}</span>
        </div>`,
    ),
  );

  $('#overdue-list').innerHTML = overdue.length
    ? toHTML(
        overdue.slice(0, 6).map(
          (l) => html`
            <div class="list-item">
              <div><b>${l.title}</b><small>${l.name} · Phiếu #${l.id} · Hạn ${l.due_on}</small></div>
              <div class="list-stack">${badge(l)}<button class="action" data-return="${l.id}">Trả sách</button></div>
            </div>
          `,
        ),
      )
    : '<p class="empty">Không có phiếu quá hạn.</p>';

  $('#top-books').innerHTML = stats.top_books.length
    ? toHTML(
        stats.top_books.map(
          (b, i) => html`<div class="list-item"><span>${i + 1}. ${b.title}</span><b>${b.count} lượt</b></div>`,
        ),
      )
    : '<p class="empty">Chưa có lượt mượn.</p>';
}
