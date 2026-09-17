// @ts-check
import { $, html, raw, toHTML } from '../dom.js';
import { icons } from '../icons.js';
import { state } from '../state.js';
import * as dashboard from './dashboard.js';
import * as books from './books.js';
import * as readers from './readers.js';
import * as loans from './loans.js';
import * as users from './users.js';

/** @typedef {import('../types.js').PageName} PageName */

/**
 * Mỗi trang gồm một module xuất `meta` (tiêu đề, nhãn menu, adminOnly) và `render()` (điền dữ liệu),
 * cùng một file views/<tên>.html là khung HTML. Thêm trang mới = viết module + file HTML, thêm vào đây,
 * thêm icon ở icons.js và tên trang vào UI_PAGES ở app/main.py.
 * Thứ tự ở đây là thứ tự trên menu.
 */
export const PAGES = { dashboard, books, readers, loans, users };

/** Tên trang → tiêu đề, cho router và <title>. @type {Record<PageName, string>} */
export const ROUTES = /** @type {Record<PageName, string>} */ (
  Object.fromEntries(Object.entries(PAGES).map(([name, page]) => [name, page.meta.title]))
);

/**
 * Dựng menu và gắn khung HTML của mọi trang (app/static/views/<tên>.html) vào #pages.
 * Gọi một lần (await) trước khi gắn sự kiện trong main.js, vì các nút trong trang chưa tồn tại trước đó.
 */
export async function mount() {
  const names = /** @type {PageName[]} */ (Object.keys(PAGES));
  const views = await Promise.all(
    names.map(async (name) => {
      const response = await fetch(`/static/views/${name}.html`);
      if (!response.ok) throw new Error(`Không tải được giao diện trang ${name}`);
      return raw(await response.text());
    }),
  );
  $('#nav').innerHTML = toHTML(
    names.map(
      (name) => html`
        <button data-page="${name}" id="nav-${name}" ${PAGES[name].meta.adminOnly ? html`data-admin hidden` : ''}>
          ${icons[name]}${PAGES[name].meta.label}
        </button>
      `,
    ),
  );
  $('#pages').innerHTML = toHTML(
    names.map(
      (name, i) =>
        html`<section id="${name}" class="page" ${name === 'dashboard' ? '' : html`hidden`}>${views[i]}</section>`,
    ),
  );
}

/** Vẽ lại trang đang mở với dữ liệu mới nhất từ server. */
export function refresh() {
  return PAGES[state.page].render();
}
