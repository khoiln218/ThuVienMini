# Kịch bản demo và câu hỏi bảo vệ

## Chuẩn bị

Chạy ứng dụng trước buổi báo cáo. Mở sẵn báo cáo PDF, slide và trình duyệt tại localhost. Đảm bảo Python và dependency đã cài để không phụ thuộc Internet tại phòng bảo vệ. Dùng `data/demo_moi.db` theo README nếu muốn dữ liệu sạch theo ngày hiện tại. Đây là đề tài **nhóm 1**, có đủ bốn thành viên trên bìa.

## Phân chia trình bày đề xuất

Đây là gợi ý phân chia cho buổi bảo vệ, không xác nhận đóng góp đã thực hiện của từng người.

| Thành viên | Nội dung trình bày | Thời lượng gợi ý |
|---|---|---|
| Phạm Tuấn Anh | Bài toán, phạm vi, yêu cầu, Use Case | 2 phút |
| Phạm Phước Hòa | Lớp phân tích, CSDL, quy tắc dữ liệu | 2 phút |
| Lê Ngọc Khôi | Kiến trúc và demo chức năng chính | 4 phút |
| Lê Bá Quảng | Kiểm thử, kết quả, hạn chế | 2 phút |

## Demo bắt buộc theo thứ tự

1. Đăng nhập `admin / Admin@123`. Chỉ ra tổng quan, nhưng dành phần lớn thời gian cho quản lý và mượn trả.
2. **Sách:** thêm mã `BV001`, tên `Sách bảo vệ`, tác giả `Nhóm 1`, thể loại `Tin học`, tổng bản `1`. Tìm `BV001`. Sửa tên thành `Sách bảo vệ nhóm 1`. Thử thêm lại mã `BV001` để chứng minh trùng mã bị chặn.
3. **Độc giả:** thêm `BV001`, họ tên `Độc giả demo`, điện thoại tùy chọn. Tìm lại và sửa tên thành `Độc giả bảo vệ`.
4. **Mượn:** chọn đúng sách và độc giả vừa tạo, thời hạn 14 ngày. Chỉ ra phiếu mới và số có sẵn giảm từ 1 về 0. Sách hết bản sẽ không còn trong danh sách chọn khi lập phiếu mới.
5. **Ràng buộc:** vào Kho sách, bấm `Ngừng` cho sách đang mượn. Hệ thống báo còn phiếu chưa trả và giữ nguyên sách.
6. **Trả:** mở Mượn & trả, bấm Trả sách cho đúng phiếu vừa lập, xác nhận đã nhận sách. Kiểm tra trạng thái Đã trả và tồn có sẵn trở lại 1.
7. **Xóa mềm:** sau khi trả, bấm Ngừng cho sách và độc giả demo. Bản ghi rời danh sách hoạt động nhưng phiếu trong lịch sử vẫn giữ tên sách và độc giả.
8. **Phần bổ sung:** lọc Quá hạn để xem phiếu mẫu. Đăng nhập `thuthu / ThuThu@123` để chỉ ra thủ thư không có nút Ngừng. Trình bày kết quả pytest thật, không chạy toàn bộ test nếu thời gian bảo vệ ngắn.

Nếu cần làm lại demo trong cùng CSDL, dùng mã BV002 vì mã xóa mềm vẫn duy nhất. Không đổi ngày máy hoặc sửa CSDL trực tiếp chỉ để tạo kết quả demo.

## Câu hỏi dự kiến

### 1. Tại sao chọn FastAPI và SQLite?

FastAPI cung cấp định tuyến và kiểm tra kiểu dữ liệu; SQLite lưu trong một file, không cần cài dịch vụ máy chủ CSDL. Phù hợp quy mô nhỏ và Windows. JavaScript thuần giúp mở giao diện mà không cần quy trình build frontend. Tất cả công cụ chạy bài là miễn phí.

### 2. Phân biệt đầu sách và bản sách thế nào?

Một dòng books mô tả một đầu sách, total là số bản vật lý thuộc đầu sách đó. Mỗi loan giữ một bản. Bản demo chưa có bảng book_copies và barcode riêng từng bản. Nếu mở rộng thì tách Book và BookCopy, loan tham chiếu copy_id.

### 3. Vì sao không lưu số có sẵn?

Số có sẵn được tính từ total và số phiếu chưa trả, tránh sai lệch giữa tồn kho và phiếu. Chỉ mục theo book_id và returned_on hỗ trợ truy vấn. Khi dữ liệu lớn cần đo hiệu năng trước khi quyết định lưu cache.

### 4. Hai thủ thư mượn bản cuối cùng cùng lúc thì sao?

LoanService mở BEGIN IMMEDIATE trước khi đọc tồn và kiểm tra giới hạn. SQLite tuần tự hóa các giao dịch ghi. Giao dịch thứ hai đọc số phiếu sau khi giao dịch đầu đã commit nên nhận lỗi hết bản. Ca I01 đã kiểm tra hai luồng và có đúng một phiếu thành công.

### 5. Nếu lỗi giữa chừng thì thế nào?

Context manager transaction rollback khi có exception và luôn đóng kết nối. Phiếu lỗi không được ghi một phần. Trong thao tác trả chỉ cập nhật cùng lúc ngày trả và người nhận.

### 6. Tại sao “xóa” lại là nút Ngừng?

Đây là xóa mềm: active=0. Nếu xóa cứng sẽ ảnh hưởng lịch sử và khóa ngoại. Khi đang có phiếu chưa trả thì từ chối, khi đã trả thì ẩn khỏi danh sách hoạt động nhưng vẫn xem được lịch sử. README công khai giới hạn chưa có chức năng khôi phục bằng giao diện.

### 7. Cách xác định quá hạn?

Ngày hôm nay lớn hơn due_on và returned_on còn rỗng thì phiếu đang quá hạn. Ngày đến hạn chưa quá hạn. Khi đã trả, độ trễ tính đến ngày trả và không tăng nữa. Các biên trước hạn, đúng hạn và sau hạn một ngày đều có unit test.

### 8. Báo cáo 49 ca Pass có ý nghĩa gì?

49 là số test instance thực thi, gồm 22 ca chức năng, 20 ca biên, 5 unit test và 2 ca tích hợp. Một test parametrized tạo nhiều lần chạy. Đây không phải bằng chứng hệ thống không còn lỗi và không đại diện cho thử tải hay kiểm toán bảo mật.

### 9. Phân biệt kiểm thử đơn vị và API?

Unit test gọi trực tiếp hàm băm/kiểm tra mật khẩu và overdue_days. API test dùng TestClient đi qua định tuyến, kiểm tra đầu vào, xác thực và CSDL tạm. Ca tích hợp đồng thời gọi LoanService với hai luồng và kiểm tra số dòng cuối cùng.

### 10. Mật khẩu và phiên đăng nhập lưu ở đâu?

Mật khẩu lưu PBKDF2-HMAC-SHA256 với salt ngẫu nhiên, không lưu bản rõ. Cookie HttpOnly chứa token ngẫu nhiên; CSDL chỉ lưu SHA256 của token và thời điểm hết hạn 8 giờ. Khi đăng xuất, server xóa phiên. Cookie SameSite strict và custom header bảo vệ yêu cầu ghi trên cùng origin.

### 11. Vì sao độc giả không đăng nhập?

Đề bài chính yêu cầu quản lý độc giả, chưa bắt buộc cổng tự phục vụ. Độc giả là đối tượng nghiệp vụ, thủ thư thao tác thay. Nếu phát triển thêm, tạo tài khoản độc giả và phân quyền xem phiếu của chính mình.

### 12. Quy tắc 5 bản và 30 ngày từ đâu?

Đó là giả định nghiệp vụ nhóm chọn cho bản triển khai vì đề gốc chỉ nêu quản lý sách, độc giả, mượn/trả. Nhóm ghi rõ trong báo cáo để giảng viên kiểm tra và có thể sửa theo quy định thư viện thực tế.

### 13. Dữ liệu có thật không?

Độc giả và số điện thoại là dữ liệu giả lập. Một số tên sách là ví dụ quen thuộc; danh mục không phải dữ liệu thư mục chuẩn hóa. Danh sách thành viên bìa lấy từ thông tin nhóm cung cấp.

### 14. Chức năng chưa có là gì?

Chưa quản lý barcode từng bản, phạt tiền, gia hạn, đặt trước, khôi phục bằng UI hoặc quản lý tài khoản bằng UI. Chưa xác nhận tải lớn, hoạt động 24/7 hay triển khai Internet. Bản hiện tại hoàn thành các luồng chính ở quy mô thư viện mini.

### 15. Giai đoạn phân tích khác thiết kế ra sao?

Phân tích mô tả khái niệm Sách, Độc giả, Phiếu mượn và tương tác nghiệp vụ. Thiết kế chỉ rõ DTO Pydantic, LoanService, module main/db, route HTTP, khóa ngoại và giao dịch. Các mô hình được đối chiếu với code, không mặc định mọi lớp khái niệm đều là Python class.

## Các điểm cần kiểm tra trước khi nộp

- Bốn tên, mã sinh viên và lớp đúng danh sách nhóm.
- Nếu trường yêu cầu tên giảng viên, khoa hoặc mẫu bìa riêng, bổ sung thông tin thật vào DOCX. Không điền giả.
- Nhóm đọc và chạy ít nhất một vòng demo, hiểu quy tắc và giới hạn đã ghi.
- Gửi cả source, database mẫu, báo cáo, slide và test results. Không gửi thư mục môi trường ảo `.venv`.
