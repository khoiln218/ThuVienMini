"""Kiểm thử giao diện thật bằng Playwright (Chromium headless) trên một server uvicorn chạy trong thread.
Chạy: .venv/bin/python -m pytest tests/test_ui.py -q
Cần cài: pip install -r requirements-dev.txt && python -m playwright install chromium
Tự bỏ qua nếu chưa cài Playwright, nên bộ test API vẫn chạy được ở máy không có trình duyệt."""
import socket
import threading
import time

import pytest

pytest.importorskip('playwright')
import uvicorn
from playwright.sync_api import expect

from app.main import app, login_guard
from seed import seed


@pytest.fixture(scope='module')
def server(tmp_path_factory):
    db = tmp_path_factory.mktemp('ui') / 'ui.db'
    import os
    os.environ['LIBRARY_DB'] = str(db)
    os.environ['LIBRARY_BACKUP'] = '0'
    seed()
    login_guard.reset()
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
    config = uvicorn.Config(app, host='127.0.0.1', port=port, log_level='warning')
    srv = uvicorn.Server(config)
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    for _ in range(50):
        if srv.started:
            break
        time.sleep(0.1)
    yield f'http://127.0.0.1:{port}'
    srv.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def signed_in(page, server):
    page.goto(server + '/')
    page.fill('input[name=username]', 'admin')
    page.fill('input[name=password]', 'Admin@123')
    page.click('#login-form button[type=submit]')
    expect(page.locator('#app-view')).to_be_visible()
    return page


def test_UI01_login_and_dashboard(signed_in):
    page = signed_in
    expect(page.locator('#user-label')).to_contain_text('admin')
    expect(page.locator('#stats .stat')).to_have_count(4)
    expect(page.locator('#overdue-list .list-item')).to_have_count(1)
    expect(page).to_have_title('Tổng quan thư viện · Thư viện mini')


def test_UI02_wrong_password_shows_error(page, server):
    page.goto(server + '/')
    page.fill('input[name=username]', 'admin')
    page.fill('input[name=password]', 'sai')
    page.click('#login-form button[type=submit]')
    expect(page.locator('#login-error')).to_contain_text('không đúng')
    expect(page.locator('#app-view')).to_be_hidden()


def test_UI03_routing_and_loan_filter(signed_in, server):
    page = signed_in
    page.click('nav button[data-page=loans]')
    expect(page).to_have_url(server + '/loans')
    page.select_option('#loan-status', 'overdue')
    expect(page).to_have_url(server + '/loans/overdue')
    expect(page.locator('#loan-rows tr')).to_have_count(1)
    expect(page.locator('#loan-rows .badge')).to_contain_text('Quá hạn')
    page.reload()
    expect(page.locator('#loan-status')).to_have_value('overdue')
    page.go_back()  # đổi bộ lọc dùng replaceState nên Back về thẳng tổng quan, không qua /loans
    expect(page).to_have_url(server + '/')
    expect(page.locator('#dashboard')).to_be_visible()
    page.goto(server + '/khong-co')
    expect(page.locator('h1')).to_have_text('Không tìm thấy trang')


def test_UI04_pagination_controls(signed_in):
    page = signed_in
    page.click('nav button[data-page=books]')
    expect(page.locator('#books-pager')).to_contain_text('Trang 1/1')
    page.select_option('#books-pager select[data-size]', '5')
    expect(page.locator('#books-pager')).to_contain_text('Trang 1/2')
    expect(page.locator('#book-rows tr')).to_have_count(5)
    page.click('#books-pager button[data-go="2"]')
    expect(page.locator('#books-pager')).to_contain_text('Trang 2/2')
    expect(page.locator('#book-rows tr')).to_have_count(3)
    page.select_option('#books-pager select[data-size]', '20')


def test_UI05_add_edit_book_escapes_html(signed_in):
    page = signed_in
    page.click('nav button[data-page=books]')
    page.click('#add-book')
    dialog = page.locator('#editor')
    expect(dialog).to_be_visible()
    page.fill('#editor input[name=code]', 'UI-XSS')
    page.fill('#editor input[name=barcode]', '8930000009999')
    page.fill('#editor input[name=title]', '<img src=x onerror=alert(1)>')
    page.fill('#editor input[name=author]', 'Kiểm thử')
    page.fill('#editor input[name=category]', 'Tin học')
    page.fill('#editor input[name=total]', '2')
    page.click('#editor button[type=submit]')
    expect(dialog).to_be_hidden()
    expect(page.locator('#notification')).to_contain_text('Đã lưu')
    cell = page.locator('#book-rows tr', has_text='UI-XSS').locator('td.text-wrap b')
    expect(cell).to_have_text('<img src=x onerror=alert(1)>')
    assert page.locator('#book-rows img').count() == 0
    # Tìm theo mã vạch (như máy quét gõ vào ô tìm kiếm rồi Enter)
    page.fill('#book-search input', '8930000009999')
    page.press('#book-search input', 'Enter')
    expect(page.locator('#book-rows tr')).to_have_count(1)
    expect(page.locator('#book-rows .barcode')).to_have_text('8930000009999')
    page.fill('#book-search input', '')
    page.press('#book-search input', 'Enter')
    # Sửa
    page.locator('#book-rows tr', has_text='UI-XSS').locator('button[data-edit-book]').click()
    expect(page.locator('#editor input[name=code]')).to_have_value('UI-XSS')
    page.fill('#editor input[name=title]', 'Đã đổi tên')
    page.click('#editor button[type=submit]')
    expect(page.locator('#book-rows tr', has_text='UI-XSS')).to_contain_text('Đã đổi tên')


def test_UI06_borrow_and_return(signed_in):
    page = signed_in
    page.click('#quick-borrow')
    page.select_option('#editor select[name=reader_id]', label='DG004 · Phạm Ngọc Mai')
    page.select_option('#editor select[name=book_id]', index=0)
    page.click('#editor button[type=submit]')
    expect(page.locator('#notification')).to_contain_text('Đã lưu')
    page.click('nav button[data-page=loans]')
    page.select_option('#loan-status', 'open')
    row = page.locator('#loan-rows tr').first
    expect(row).to_contain_text('Đang mượn')
    page.once('dialog', lambda d: d.accept())
    row.locator('button[data-return]').click()
    expect(page.locator('#notification')).to_contain_text('Đã ghi nhận trả sách')


def test_UI07_change_password_and_relogin(signed_in, server):
    page = signed_in
    page.click('#change-password')
    page.fill('#editor input[name=current_password]', 'Admin@123')
    page.fill('#editor input[name=new_password]', 'Admin@456')
    page.fill('#editor input[name=confirm]', 'Admin@999')
    page.click('#editor button[type=submit]')
    expect(page.locator('#editor-error')).to_contain_text('không khớp')
    page.fill('#editor input[name=confirm]', 'Admin@456')
    page.click('#editor button[type=submit]')
    expect(page.locator('#editor')).to_be_hidden()
    page.click('#logout')
    expect(page.locator('#login-view')).to_be_visible()
    page.fill('input[name=username]', 'admin')
    page.fill('input[name=password]', 'Admin@456')
    page.click('#login-form button[type=submit]')
    expect(page.locator('#app-view')).to_be_visible()
    # Trả lại mật khẩu demo cho các test sau
    page.click('#change-password')
    page.fill('#editor input[name=current_password]', 'Admin@456')
    page.fill('#editor input[name=new_password]', 'Admin@123')
    page.fill('#editor input[name=confirm]', 'Admin@123')
    page.click('#editor button[type=submit]')
    expect(page.locator('#editor')).to_be_hidden()


def test_UI08_librarian_has_no_admin_controls(page, server):
    page.goto(server + '/users')
    page.fill('input[name=username]', 'thuthu')
    page.fill('input[name=password]', 'ThuThu@123')
    page.click('#login-form button[type=submit]')
    expect(page.locator('#app-view')).to_be_visible()
    expect(page).to_have_url(server + '/')
    expect(page.locator('#nav-users')).to_be_hidden()
    expect(page.locator('#backup')).to_be_hidden()
    page.click('nav button[data-page=books]')
    expect(page.locator('#book-rows button[data-remove]')).to_have_count(0)


def test_UI09_reload_keeps_page_without_login_flash(signed_in, server):
    page = signed_in
    page.click('nav button[data-page=books]')
    expect(page.locator('#book-rows tr').first).to_be_visible()
    # Chặn /api/me để giữ trạng thái "đang tải" và nhìn xem màn hình đăng nhập có lộ ra không
    page.route('**/api/me', lambda route: (page.wait_for_timeout(300), route.continue_()))
    page.reload()
    assert page.evaluate("document.querySelector('#login-view').hidden") is True
    expect(page.locator('#app-view')).to_be_visible()
    expect(page.locator('#books')).to_be_visible()
    expect(page).to_have_url(server + '/books')
