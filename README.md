# BTL nhóm 1 — Quản lý thư viện mini

Web application chạy tại máy, không có dịch vụ trả phí. Python FastAPI + SQLite + HTML/CSS/JavaScript thuần. Hoàn thành các chức năng chính: quản lý sách, quản lý độc giả, mượn và trả sách. Có đăng nhập, tìm kiếm, lọc quá hạn và thống kê.

## Thành viên

| Mã SV | Họ tên | Lớp |
|---|---|---|
| B24DTCN057 | Phạm Tuấn Anh | D24TXCN06-B |
| B24DTCN060 | Phạm Phước Hòa | D24TXCN06-B |
| B24DTCN061 | Lê Ngọc Khôi | D24TXCN06-B |
| K25DTCN499 | Lê Bá Quảng | D25TXCN14-K |

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11+ (kiểm thử với 3.12) |
| Backend | FastAPI 0.141 trên Starlette 1.6, chạy bằng Uvicorn 0.53 |
| Kiểm tra dữ liệu | Pydantic v2 (`app/models.py`) |
| Cơ sở dữ liệu | SQLite qua module chuẩn `sqlite3`, `PRAGMA foreign_keys=ON`, giao dịch tường minh (`app/db.py`, `schema.sql`) |
| Xác thực | Thư viện chuẩn: `hashlib.pbkdf2_hmac` (SHA-256, 260 000 vòng) băm mật khẩu, `secrets` sinh token, session lưu trong CSDL, cookie `HttpOnly` + `SameSite=Strict`, khóa tạm sau 5 lần sai mật khẩu |
| Frontend | HTML / CSS / JavaScript thuần (ES modules, `@ts-check` + JSDoc), một trang, gọi API bằng `fetch`; không framework, không CDN, không bước build |
| Công cụ frontend (chỉ dev) | Prettier, ESLint, TypeScript (kiểm tra kiểu file .js) qua `npm run check`; Playwright cho test giao diện |
| Kiểm thử | pytest 9 + `fastapi.testclient` (httpx); test API, unit, boundary, concurrency, migration; pytest-playwright cho 8 luồng giao diện trên Chromium; xuất JUnit XML |
| Tài liệu | PlantUML (11 sơ đồ), báo cáo Markdown/DOCX/PDF |
| Khởi động | `start.bat` (Windows), `start.sh` (macOS/Linux), `venv` + `pip` |

Các gói khác trong `requirements.txt` (anyio, h11, httpcore, click, certifi, ...) là phụ thuộc gián tiếp của FastAPI/Uvicorn/httpx/pytest.

## Chạy nhanh trên Windows

1. Cài Python 3.11 trở lên từ https://www.python.org/downloads/windows/ (đã kiểm thử với Python 3.12). Bật Python Launcher `py` khi cài.
2. Giải nén toàn bộ bộ nộp. Mở thư mục `ThuVienMini`, nhấp đúp `start.bat`.
3. Lần đầu cần Internet để tải các thư viện miễn phí. Khi thấy `Uvicorn running`, mở http://127.0.0.1:8000.
4. Giữ cửa sổ chạy máy chủ mở trong lúc demo. Nhấn Ctrl+C để dừng.

### Tài khoản mẫu

| Vai trò | Tên đăng nhập | Mật khẩu demo |
|---|---|---|
| Quản trị viên | admin | Admin@123 |
| Thủ thư | thuthu | ThuThu@123 |

Quản trị có toàn bộ quyền. Thủ thư được thêm, sửa, tìm sách/độc giả, mượn/trả/gia hạn, xuất CSV và xem thống kê; chỉ quản trị được xóa mềm (nút **Ngừng**), quản lý tài khoản (trang **Tài khoản**) và sao lưu. Mọi người dùng tự đổi mật khẩu bằng nút **Mật khẩu** ở góc trái dưới. Tài khoản này dùng cho bài tập trên localhost, không phải tài khoản thật; hãy đổi mật khẩu ngay nếu dùng thật.

### Chạy bằng PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Không cần `Activate.ps1` nên không phải đổi ExecutionPolicy. Nếu không có lệnh `py`, thay bằng `python`. Nếu cổng 8000 bận, dùng `--port 8001` và mở đúng cổng. Nếu Python quá cũ gây lỗi cài dependency, tạo lại môi trường ảo bằng Python 3.12.

### Chạy lại khi đã cài xong, không cần mạng

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Giao diện chính không tải CDN/font hay gọi dịch vụ ngoài. `/docs` là trang API mặc định của FastAPI và có thể cần mạng để tải Swagger UI; `/openapi.json` và ứng dụng chính vẫn chạy offline.

## Chạy trên macOS / Linux

1. Cài Python 3.11 trở lên (macOS: `brew install python` hoặc tải từ python.org).
2. Mở Terminal trong thư mục `ThuVienMini` và chạy:

```bash
./start.sh
```

Script tạo `.venv`, cài thư viện (lần đầu cần Internet), chạy `seed.py` rồi khởi động máy chủ. Khi thấy `Uvicorn running`, mở http://127.0.0.1:8000. Nhấn Ctrl+C để dừng. Nếu cổng 8000 bận: `PORT=8001 ./start.sh`. Nếu báo "Permission denied", chạy `chmod +x start.sh` một lần.

Chạy lại khi đã cài xong, không cần mạng:

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Phát triển bằng VS Code

Thư mục `.vscode/` đã có sẵn cấu hình; mở thư mục `ThuVienMini` bằng **File → Open Folder** là dùng được.

1. Cài extension được gợi ý khi VS Code hỏi (Python, Debugpy, Pylance, SQLite Viewer, PlantUML, REST Client).
2. **Terminal → Run Task → "Cài môi trường (venv + pip)"** một lần. VS Code tự chọn `.venv` làm interpreter (góc phải dưới hiện `.venv`).
3. **Run and Debug (F5) → "Chạy server (tự tải lại khi sửa code)"**: uvicorn chạy với `--reload`, lưu file Python là server tự khởi động lại; đặt breakpoint trong `app/*.py` để dừng và xem biến. Sửa HTML/CSS/JS chỉ cần tải lại trình duyệt.
4. Cấu hình **"Chạy server với CSDL demo riêng"** dùng `data/dev.db` ở cổng 8001 và tắt sao lưu tự động, để thử nghiệm không đụng `data/library.db` nộp bài.
5. **Testing** (biểu tượng ống nghiệm ở thanh bên): chạy/debug từng test bằng nút ▶ cạnh tên hàm. Task "Chạy test + xuất JUnit" (`Cmd/Ctrl+Shift+B` → chọn test) tái tạo `docs/test-results.xml`.
6. `requests.http`: gọi thử từng API ngay trong editor bằng REST Client, cookie phiên được giữ sau khi đăng nhập.
7. Mở `data/library.db` bằng SQLite Viewer để xem bảng; mở `docs/uml/*.puml` và bấm `Alt+D` để xem sơ đồ PlantUML.

## Phát triển frontend

Frontend là JavaScript thuần chia thành ES modules trong `app/static/js/`, trình duyệt nạp trực tiếp — không có bước build, bản nộp không cần Node. Node chỉ dùng cho công cụ kiểm tra mã ở máy dev:

```bash
npm install          # một lần
npm run format       # Prettier định dạng js/css/html
npm run lint         # ESLint
npm run typecheck    # TypeScript kiểm tra kiểu trên file .js nhờ // @ts-check + JSDoc (types.js)
npm run check        # cả ba, dùng trước khi commit
```

Quy ước:
- Tạo HTML bằng tagged template `html\`...\`` trong `dom.js`: mọi giá trị chèn vào được thoát tự động, chỉ `raw()` cho hằng số tin cậy. Gán vào `innerHTML` qua `toHTML()`.
- Mỗi màn hình gồm một file HTML trong `views/` (khung, không có logic) và một module trong `pages/` xuất `meta` (tiêu đề, nhãn menu, `adminOnly`) và `render()` (điền dữ liệu). `pages/index.js` tải các file `views/*.html` bằng `fetch` lúc khởi động, dựng menu và gắn vào `#pages`; `main.js` `await mount()` rồi mới gắn sự kiện. Thêm màn hình mới = viết `views/x.html` + `pages/x.js`, thêm vào `PAGES`, thêm icon ở `icons.js` và tên trang vào `UI_PAGES` trong `app/main.py`.
- Phần tử chỉ dành cho quản trị đánh dấu `data-admin`; `main.js` ẩn/hiện chung sau khi đăng nhập.
- Nút sinh động trong bảng dùng thuộc tính `data-*`; `main.js` bắt sự kiện chung một lần (event delegation).
- Hộp thoại lưu xong phát sự kiện `data-changed` để trang tự vẽ lại.
- Đổi file frontend thì tăng `?v=` ở thẻ `<script>`/`<link>` trong `index.html` nếu muốn ép trình duyệt tải lại; server đã gửi `Cache-Control: no-cache` nên thường không cần.

## Dữ liệu và quy tắc

- CSDL `data/library.db` được cung cấp sẵn. `seed.py` chỉ tạo mẫu khi chưa có người dùng, không xóa dữ liệu đang có.
- Mẫu ban đầu: 2 tài khoản, 8 đầu sách / 29 bản, 4 độc giả, 5 phiếu (3 chưa trả, 2 đã trả). Một phiếu quá hạn tại ngày tạo mẫu. Ngày quá hạn thay đổi theo ngày máy chủ.
- Một phiếu tương ứng một bản sách, không quản lý mã vạch từng bản vật lý. Một độc giả được giữ tối đa 5 bản, có thể mượn nhiều bản cùng đầu sách.
- Hạn mượn 1–30 ngày, mặc định 14. Ngày hạn trả vẫn trong hạn. Quá hạn = số ngày dương từ hạn trả đến ngày hiện tại, hoặc đến ngày trả nếu đã trả.
- Cho phép độc giả đang có phiếu quá hạn tiếp tục mượn nếu còn dưới 5 bản. Bản demo chưa áp dụng phạt tiền/đặt trước.
- Gia hạn: phiếu còn trong hạn được gia hạn đúng một lần, thêm 1–30 ngày tính từ hạn trả hiện tại. Phiếu quá hạn phải trả sách trước.
- Số có sẵn = tổng bản − số phiếu chưa trả. Không lưu tồn có sẵn riêng nên không có hai nguồn số liệu.
- Không giảm tổng bản xuống dưới số đang mượn. Chặn xóa mềm sách/độc giả khi còn phiếu chưa trả. Lịch sử luôn được giữ.
- Mã sách và độc giả là duy nhất trong cả bản ghi hoạt động và đã xóa mềm, có phân biệt chữ hoa/thường. Tìm kiếm không phân biệt hoa/thường Unicode nhưng có phân biệt dấu tiếng Việt; lọc và phân trang thực hiện ngay trong SQL (`LIMIT/OFFSET`).
- Phân trang: thanh "N bản ghi · Trang x/y" dưới các bảng sách, độc giả, phiếu; chọn 5/10/20/50 dòng mỗi trang (mặc định 20, ghi nhớ trong trình duyệt). API nhận `page` (từ 1) và `size` (1–100); không truyền `page` thì trả toàn bộ danh sách (dùng cho hộp chọn khi lập phiếu và xuất CSV).
- Ngày nghiệp vụ lấy theo ngày máy chạy server. Phiên đăng nhập có hạn 8 giờ; đổi mật khẩu hoặc ngừng tài khoản sẽ hủy các phiên khác của tài khoản đó.
- Tài khoản: tên đăng nhập 3–50 ký tự chữ/số/`._-`, mật khẩu tối thiểu 8 ký tự. Không thể tự hạ quyền/tự ngừng, và luôn phải còn ít nhất một quản trị viên hoạt động. Sai mật khẩu 5 lần trong 15 phút sẽ bị khóa tạm 15 phút cho cặp tài khoản–địa chỉ đó (đếm trong bộ nhớ, khởi động lại server sẽ xóa).
- Xuất CSV (UTF-8 có BOM, mở được bằng Excel) cho sách, độc giả và toàn bộ phiếu từ nút **Xuất CSV** trên mỗi trang.

## Định tuyến

**Giao diện** (một trang, định tuyến bằng History API trong `app/static/app.js`; server trả `index.html` cho các đường dẫn dưới đây nên tải lại trang hoặc Back/Forward vẫn giữ đúng màn hình):

| URL | Màn hình |
|---|---|
| `/` | Tổng quan (mặc định) |
| `/books`, `/readers` | Kho sách, Độc giả |
| `/loans`, `/loans/open`, `/loans/overdue`, `/loans/returned` | Mượn & trả với bộ lọc tương ứng |
| `/users` | Tài khoản (chỉ admin; người khác bị đưa về tổng quan) |
| đường dẫn khác | Trang 404 có giao diện (`app/static/views/404.html`); với `/api/*` vẫn trả JSON 404 |

**API** (`app/main.py`; mọi route trừ đăng nhập cần cookie phiên, thao tác ghi cần header `X-Library-Request: 1`):

| Phương thức, đường dẫn | Quyền | Chức năng |
|---|---|---|
| `POST /api/login`, `POST /api/logout`, `GET /api/me` | — / đã đăng nhập | Phiên làm việc |
| `POST /api/password` | đã đăng nhập | Đổi mật khẩu của chính mình |
| `GET/POST /api/users`, `PUT /api/users/{id}` | admin | Quản lý tài khoản |
| `GET/POST /api/books`, `PUT /api/books/{id}` | đã đăng nhập | Sách; `GET` nhận `q`, `page`, `size` |
| `GET/POST /api/readers`, `PUT /api/readers/{id}` | đã đăng nhập | Độc giả; `GET` nhận `q`, `page`, `size` |
| `DELETE /api/{books\|readers}/{id}` | admin | Ngừng hoạt động (xóa mềm) |
| `GET/POST /api/loans` | đã đăng nhập | Phiếu; `GET` nhận `status`, `page`, `size` |
| `POST /api/loans/{id}/return`, `POST /api/loans/{id}/extend` | đã đăng nhập | Trả sách, gia hạn |
| `GET /api/stats` | đã đăng nhập | Thống kê |
| `GET /api/export/{books\|readers\|loans}.csv` | đã đăng nhập | Xuất CSV |
| `POST /api/backup` | admin | Sao lưu CSDL |
| `GET /docs`, `GET /openapi.json` | — | Tài liệu API tự sinh của FastAPI |

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=docs/test-results.xml
```

Test giao diện (`tests/test_ui.py`) dùng Playwright điều khiển Chromium thật trên một server uvicorn chạy trong thread với CSDL tạm. Cần cài thêm một lần (có Internet): `pip install -r requirements-dev.txt` rồi `python -m playwright install chromium`. Máy chưa cài Playwright thì các test này tự bỏ qua, phần API vẫn chạy.

70 ca tự động đã đạt trong lần kiểm thử cung cấp (62 API/unit + 8 giao diện Playwright). `docs/test-results.xml` là kết quả pytest thật; `docs/ket_qua_kiem_thu.csv` là bảng từng ca. Test dùng database tạm riêng, không đụng dữ liệu demo. Chi tiết ca kiểm thử và giới hạn kiểm chứng nằm trong báo cáo. Hai cảnh báo deprecation từ thư viện kiểm thử được giữ trong log, không phải ca thất bại.

## Cấu trúc

```text
app/main.py          HTTP endpoints, xác thực, CRUD
app/models.py        Pydantic DTO và ràng buộc đầu vào
app/services.py      LoanService, tính quá hạn
app/db.py            Kết nối và giao dịch SQLite
app/security.py      Băm mật khẩu và token
app/static/          index.html (khung: đăng nhập, sidebar, header, dialog), style.css, logo.svg
app/static/views/    Khung HTML từng màn hình (dashboard, books, readers, loans, users) tải lúc khởi động, và 404.html (trang lỗi độc lập)
app/static/js/       Frontend chia module: main.js (điểm vào), api.js, dom.js, state.js, router.js, icons.js, types.js
app/static/js/pages/ Mỗi màn hình một module xuất meta + render(): dashboard, books, readers, loans, users; pager dùng chung
package.json, eslint.config.js, jsconfig.json, .prettierrc  Công cụ frontend (không cần để chạy app)
schema.sql           DDL, khóa ngoại và chỉ mục
seed.py              Dữ liệu mẫu không ghi đè
start.bat, start.sh  Script khởi động Windows / macOS-Linux
.vscode/, requests.http  Cấu hình VS Code (debug, task, test) và mẫu gọi API
data/library.db      Database demo
tests/               API, unit, boundary, concurrency tests
docs/uml/            11 sơ đồ PNG và nguồn PlantUML
docs/                Báo cáo, slide, bảng kiểm thử, kịch bản bảo vệ
```

## Sao lưu và tạo demo mới an toàn

Server tự sao lưu vào `data/backups/library-<ngày>-<giờ>.db` mỗi lần khởi động và khi quản trị bấm **Sao lưu dữ liệu** ở trang Tổng quan; chỉ giữ 10 bản mới nhất. Sao lưu dùng API backup của SQLite nên an toàn khi server đang chạy. Đặt biến môi trường `LIBRARY_BACKUP=0` để tắt sao lưu tự động. Để phục hồi: dừng server, chép bản sao lưu đè lên `data/library.db`.

Có thể tạo một database khác mà giữ nguyên bản cũ:

```powershell
$env:LIBRARY_DB = "$PWD\data\demo_moi.db"
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Để trở về database mặc định trong cửa sổ PowerShell: `Remove-Item Env:LIBRARY_DB`. Không cần xóa database cũ. Khi chuyển sang database mới, đăng nhập lại vì cookie phiên cũ không nằm trong CSDL mới.

## Phạm vi triển khai

Bản nộp phù hợp thư viện mini và trình diễn tại máy. Đã có quản lý tài khoản, đổi mật khẩu, gia hạn, xuất CSV, phân trang, sao lưu tự động và chống dò mật khẩu cơ bản. Chưa đo tải lớn, chưa có phục hồi dữ liệu bằng giao diện, quản lý bản sách theo barcode, phạt tiền/đặt trước hoặc cấu hình HTTPS. Không tự công khai máy chủ lên Internet; nếu dùng trong mạng LAN cần đặt reverse proxy HTTPS phía trước. Khi triển khai thật cần bổ sung các phần này và đổi tài khoản demo.

## Tài liệu căn cứ

- Đề gốc: https://docs.google.com/document/d/1Z4gQx6iHjog6jNRzuYSzWolWmAVAnrvO/edit
- FastAPI TestClient: https://fastapi.tiangolo.com/tutorial/testing/
- SQLite transactions: https://www.sqlite.org/lang_transaction.html
- Các quy định về 5 bản / 1–30 ngày là giả định của bài triển khai, không phải yêu cầu được trích nguyên văn từ đề gốc.
