// @ts-check
// Icon SVG inline cho menu: nét 1.8px, stroke=currentColor nên đổi màu theo trạng thái nút (xem nav button .icon trong style.css).
import { html, raw } from './dom.js';

/** @param {string} shapes  Các phần tử <path>/<rect>/<circle> trong hệ toạ độ 24x24 */
const icon = (shapes) =>
  html`<svg
    class="icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    ${raw(shapes)}
  </svg>`;

/** @type {Record<import('./types.js').PageName, ReturnType<typeof html>>} */
export const icons = {
  dashboard: icon(
    '<rect x="3" y="3" width="8" height="8" rx="1.5" /><rect x="13" y="3" width="8" height="5" rx="1.5" /><rect x="13" y="11" width="8" height="10" rx="1.5" /><rect x="3" y="14" width="8" height="7" rx="1.5" />',
  ),
  books: icon(
    '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z" /><path d="M4 18a2.5 2.5 0 0 1 2.5-2.5H20" /><path d="M8 7h8" />',
  ),
  readers: icon(
    '<circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0" /><circle cx="17" cy="9.5" r="2.5" /><path d="M15.5 15.2a5 5 0 0 1 6 4.8" />',
  ),
  loans: icon('<path d="M4 8h13l-3-3" /><path d="M20 16H7l3 3" />'),
  users: icon(
    '<path d="M12 3l7 3v5c0 4.5-3 8.2-7 10-4-1.8-7-5.5-7-10V6z" /><circle cx="12" cy="10.5" r="2.5" /><path d="M8.5 17a4 4 0 0 1 7 0" />',
  ),
};
