# BTL nhóm 1 — Quản lý thư viện mini

Web application chạy tại máy, không có dịch vụ trả phí. Python FastAPI + SQLite + HTML/CSS/JavaScript thuần. Hoàn thành các chức năng chính: quản lý sách, quản lý độc giả, mượn và trả sách. Có đăng nhập, tìm kiếm, lọc quá hạn và thống kê.

## Thành viên

| Mã SV | Họ tên | Lớp |
|---|---|---|
| B24DTCN057 | Phạm Tuấn Anh | D24TXCN06-B |
| B24DTCN060 | Phạm Phước Hòa | D24TXCN06-B |
| B24DTCN061 | Lê Ngọc Khôi | D24TXCN06-B |
| K25DTCN499 | Lê Bá Quảng | D25TXCN14-K |

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

Quản trị có toàn bộ quyền. Thủ thư được thêm, sửa, tìm sách/độc giả, mượn/trả và xem thống kê; chỉ quản trị được xóa mềm (nút **Ngừng**). Tài khoản này dùng cho bài tập trên localhost, không phải tài khoản thật.

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

## Dữ liệu và quy tắc

- CSDL `data/library.db` được cung cấp sẵn. `seed.py` chỉ tạo mẫu khi chưa có người dùng, không xóa dữ liệu đang có.
- Mẫu ban đầu: 2 tài khoản, 8 đầu sách / 29 bản, 4 độc giả, 5 phiếu (3 chưa trả, 2 đã trả). Một phiếu quá hạn tại ngày tạo mẫu. Ngày quá hạn thay đổi theo ngày máy chủ.
- Một phiếu tương ứng một bản sách, không quản lý mã vạch từng bản vật lý. Một độc giả được giữ tối đa 5 bản, có thể mượn nhiều bản cùng đầu sách.
- Hạn mượn 1–30 ngày, mặc định 14. Ngày hạn trả vẫn trong hạn. Quá hạn = số ngày dương từ hạn trả đến ngày hiện tại, hoặc đến ngày trả nếu đã trả.
- Cho phép độc giả đang có phiếu quá hạn tiếp tục mượn nếu còn dưới 5 bản. Bản demo chưa áp dụng phạt tiền/gia hạn/đặt trước.
- Số có sẵn = tổng bản − số phiếu chưa trả. Không lưu tồn có sẵn riêng nên không có hai nguồn số liệu.
- Không giảm tổng bản xuống dưới số đang mượn. Chặn xóa mềm sách/độc giả khi còn phiếu chưa trả. Lịch sử luôn được giữ.
- Mã sách và độc giả là duy nhất trong cả bản ghi hoạt động và đã xóa mềm, có phân biệt chữ hoa/thường. Tìm kiếm không phân biệt hoa/thường Unicode nhưng có phân biệt dấu tiếng Việt.
- Ngày nghiệp vụ lấy theo ngày máy Windows chạy server. Phiên đăng nhập có hạn 8 giờ.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=docs/test-results.xml
```

49 ca tự động đã đạt trong lần kiểm thử cung cấp. `docs/test-results.xml` là kết quả pytest thật; `docs/ket_qua_kiem_thu.csv` là bảng từng ca. Test dùng database tạm riêng, không đụng dữ liệu demo. Chi tiết ca kiểm thử và giới hạn kiểm chứng nằm trong báo cáo. Hai cảnh báo deprecation từ thư viện kiểm thử được giữ trong log, không phải ca thất bại.

## Cấu trúc

```text
app/main.py          HTTP endpoints, xác thực, CRUD
app/models.py        Pydantic DTO và ràng buộc đầu vào
app/services.py      LoanService, tính quá hạn
app/db.py            Kết nối và giao dịch SQLite
app/security.py      Băm mật khẩu và token
app/static/          HTML, CSS, JavaScript
schema.sql           DDL, khóa ngoại và chỉ mục
seed.py              Dữ liệu mẫu không ghi đè
start.bat, start.sh  Script khởi động Windows / macOS-Linux
data/library.db      Database demo
tests/               API, unit, boundary, concurrency tests
docs/uml/            11 sơ đồ PNG và nguồn PlantUML
docs/                Báo cáo, slide, bảng kiểm thử, kịch bản bảo vệ
```

## Sao lưu và tạo demo mới an toàn

Dừng server rồi sao chép `data/library.db` sang tên khác để sao lưu. Có thể tạo một database khác mà giữ nguyên bản cũ:

```powershell
$env:LIBRARY_DB = "$PWD\data\demo_moi.db"
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Để trở về database mặc định trong cửa sổ PowerShell: `Remove-Item Env:LIBRARY_DB`. Không cần xóa database cũ. Khi chuyển sang database mới, đăng nhập lại vì cookie phiên cũ không nằm trong CSDL mới.

## Phạm vi triển khai

Bản nộp phù hợp thư viện mini và trình diễn tại máy. Chưa đo tải lớn, chưa có phục hồi dữ liệu bằng giao diện, quản lý tài khoản bằng giao diện, quản lý bản sách theo barcode, chống dò mật khẩu hoặc cấu hình HTTPS. Không tự công khai máy chủ lên Internet. Khi triển khai thật cần bổ sung các phần này và đổi tài khoản demo.

## Tài liệu căn cứ

- Đề gốc: https://docs.google.com/document/d/1Z4gQx6iHjog6jNRzuYSzWolWmAVAnrvO/edit
- FastAPI TestClient: https://fastapi.tiangolo.com/tutorial/testing/
- SQLite transactions: https://www.sqlite.org/lang_transaction.html
- Các quy định về 5 bản / 1–30 ngày là giả định của bài triển khai, không phải yêu cầu được trích nguyên văn từ đề gốc.
