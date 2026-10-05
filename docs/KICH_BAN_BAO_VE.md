# Kịch bản demo và câu hỏi bảo vệ

## Chuẩn bị

Chạy ứng dụng trước buổi báo cáo (`start.bat` hoặc `./start.sh`). Mở sẵn báo cáo PDF và trình duyệt tại localhost. Đảm bảo Python và dependency đã cài để không phụ thuộc Internet tại phòng bảo vệ. CSDL nộp kèm là bộ demo (63 sách, 60 độc giả, 200 phiếu / 328 cuốn); muốn ngày mượn tính lại theo hôm nay thì dừng server và chạy `python seed.py --force`. Có thể mở thêm link Vercel làm phương án dự phòng nếu máy trục trặc (nhớ rằng dữ liệu trên đó không lưu bền). Đây là đề tài **nhóm 1**, có đủ bốn thành viên trên bìa.

## Phân chia trình bày đề xuất

Đây là gợi ý phân chia cho buổi bảo vệ, không xác nhận đóng góp đã thực hiện của từng người.

| Thành viên | Nội dung trình bày | Thời lượng gợi ý |
|---|---|---|
| Phạm Tuấn Anh | Bài toán, phạm vi, quy trình, yêu cầu, Use Case (Chương I, II, III.I) | 3 phút |
| Phạm Phước Hòa | Sơ đồ hoạt động, ERD, CSDL, giao diện, xử lý (Chương III.II–V) | 3 phút |
| Lê Ngọc Khôi | Demo chức năng chính (Chương IV) | 3 phút |
| Lê Bá Quảng | Cài đặt, thử nghiệm, kết luận, hạn chế (Chương V, VI) | 3 phút |

Lời thoại chi tiết theo từng mốc thời gian: `KICH_BAN_TRINH_BAY.md`. Phần "Demo bắt buộc" dưới đây là bản đầy đủ dùng khi có thêm thời gian hoặc khi giảng viên yêu cầu xem thêm.

## Demo bắt buộc theo thứ tự

1. Đăng nhập `admin / Admin@123`. Chỉ ra tổng quan, nhưng dành phần lớn thời gian cho quản lý và mượn trả.
2. **Sách:** thêm mã `BV001`, tên `Sách bảo vệ`, tác giả `Nhóm 1`, thể loại `Tin học`, tổng bản `1`; thêm tiếp `BV002` tổng bản `2`. Tìm `BV001`. Sửa tên thành `Sách bảo vệ nhóm 1`. Thử thêm lại mã `BV001` để chứng minh trùng mã bị chặn.
3. **Độc giả:** thêm `BV001`, họ tên `Độc giả demo`, điện thoại tùy chọn. Tìm lại và sửa tên thành `Độc giả bảo vệ`.
4. **Mượn:** Lập phiếu mượn cho độc giả vừa tạo, đánh dấu cả `BV001` và `BV002` (dùng ô lọc), 14 ngày, để chọn ô "In phiếu ngay sau khi lập". Chỉ ra thông báo "Đã lập phiếu mượn #n gồm 2 cuốn", hộp thoại in mở ra với phiếu mượn có chỗ ký (chọn Lưu PDF hoặc Hủy), phiếu có hai cuốn và số có sẵn của BV001 giảm từ 1 về 0. Sách hết bản sẽ không còn trong danh sách chọn khi lập phiếu mới.
5. **Ràng buộc:** vào Kho sách, bấm `Lưu trữ` cho sách đang mượn. Hệ thống báo "Còn sách chưa trả, không thể lưu trữ" và giữ nguyên sách.
6. **Trả:** mở Mượn & trả, bấm Trả sách cho phiếu vừa lập, bỏ chọn BV002 rồi xác nhận: thông báo "phiếu còn 1 cuốn chưa trả", BV001 có sẵn trở lại 1. Trả tiếp BV002: "phiếu đã trả đủ", phiếu chuyển Đã trả.
7. **Lưu trữ:** sau khi trả, bấm Lưu trữ cho sách và độc giả demo. Bản ghi rời danh sách hoạt động nhưng phiếu trong lịch sử vẫn giữ tên sách và độc giả.
8. **Gia hạn:** ở Mượn & trả, lọc "Đang mượn trong hạn", bấm Gia hạn một phiếu (7 ngày), thấy hạn lùi và nhãn Đã gia hạn; nút Gia hạn biến mất vì chỉ được một lần. Phiếu quá hạn không có nút này.
9. **Tìm kiếm và phân trang:** ở Kho sách, tìm theo tên hoặc ISBN. Chọn "5 dòng" ở thanh phân trang, bấm Sau. Bấm "Tải danh sách (Excel)" và mở file bằng Excel nếu có.
10. **Tài khoản (admin):** trang Tài khoản → Thêm tài khoản `demo_bv` vai trò thủ thư, có họ tên và email. Ở tab ẩn danh đăng nhập bằng tài khoản đó, rồi quay lại bấm Ngừng: tab kia bị đăng xuất ngay. Bấm Sao lưu dữ liệu ở Tổng quan, chỉ file trong `data/backups/`.
11. **Phần bổ sung:** gõ URL `/loans/overdue` để thấy bộ lọc theo đường dẫn; gõ `/abc` để thấy trang 404. Đăng nhập `thuthu / ThuThu@123` để chỉ ra thủ thư không có nút Lưu trữ, menu Tài khoản và nút Sao lưu. Trình bày kết quả pytest thật (80 lần chạy, gồm 10 ca giao diện Playwright), không chạy toàn bộ test nếu thời gian bảo vệ ngắn.

Nếu cần làm lại demo trong cùng CSDL, dùng mã BV002 vì mã đã lưu trữ vẫn duy nhất. Không đổi ngày máy hoặc sửa CSDL trực tiếp chỉ để tạo kết quả demo.

## Câu hỏi dự kiến

### 1. Tại sao chọn FastAPI và SQLite?

FastAPI cung cấp định tuyến và kiểm tra kiểu dữ liệu; SQLite lưu trong một file, không cần cài dịch vụ máy chủ CSDL. Phù hợp quy mô nhỏ, chạy được Windows/macOS/Linux. JavaScript thuần chia ES modules giúp mở giao diện mà không cần bước build; Node chỉ dùng ở máy dev để format/lint/kiểm tra kiểu. Tất cả công cụ chạy bài là miễn phí.

### 2. Phân biệt đầu sách và bản sách thế nào?

Một dòng books mô tả một đầu sách, total là số bản vật lý thuộc đầu sách đó; cột barcode là ISBN/EAN-13 in trên bìa, chung cho mọi bản của đầu sách và dùng để tìm nhanh bằng máy quét. Mỗi loan giữ một bản. Bản này chưa có bảng book_copies với mã riêng từng bản. Nếu mở rộng thì tách Book và BookCopy, loan tham chiếu copy_id.

### 3. Vì sao không lưu số có sẵn?

Số có sẵn được tính từ total và số dòng chi tiết phiếu chưa trả, tránh sai lệch giữa tồn kho và phiếu. Chỉ mục loan_items(book_id, returned_on) hỗ trợ truy vấn; lọc, tìm kiếm và phân trang đều làm trong SQL nên không tải cả bảng lên Python. Khi dữ liệu lớn cần đo hiệu năng trước khi quyết định lưu cache.

### 4. Hai thủ thư mượn bản cuối cùng cùng lúc thì sao?

LoanService mở BEGIN IMMEDIATE trước khi đọc tồn và kiểm tra giới hạn. SQLite tuần tự hóa các giao dịch ghi. Giao dịch thứ hai đọc số cuốn đang mượn sau khi giao dịch đầu đã commit nên nhận lỗi hết bản. Ca I01 đã kiểm tra hai luồng và có đúng một phiếu thành công.

### 5. Nếu lỗi giữa chừng thì thế nào?

Context manager transaction rollback khi có exception và luôn đóng kết nối. Phiếu lỗi không được ghi một phần. Trong thao tác trả chỉ cập nhật cùng lúc ngày trả và người nhận.

### 6. Tại sao “xóa” lại là nút Ngừng?

Đây là lưu trữ: đặt active=0, hồ sơ ẩn khỏi danh sách nhưng không bị xóa. Nếu xóa hẳn sẽ ảnh hưởng lịch sử và khóa ngoại. Khi đang có phiếu chưa trả thì từ chối, khi đã trả thì ẩn khỏi danh sách hoạt động nhưng vẫn xem được lịch sử và trong CSV. README công khai giới hạn chưa có chức năng xem lại hồ sơ đã lưu trữ hay khôi phục bằng giao diện; tài khoản thì có Kích hoạt lại.

### 7. Cách xác định quá hạn?

Ngày hôm nay lớn hơn due_on và returned_on còn rỗng thì phiếu đang quá hạn. Ngày đến hạn chưa quá hạn. Khi đã trả, độ trễ tính đến ngày trả và không tăng nữa. Các biên trước hạn, đúng hạn và sau hạn một ngày đều có unit test.

### 8. Báo cáo 80 lần chạy đạt có ý nghĩa gì?

Bản cuối có 80 lần chạy: 43 ca chức năng API, 20 ca biên, 5 unit test, 2 ca tích hợp và 10 ca giao diện Playwright trên Chromium thật. Một test parametrized tạo nhiều lần chạy. Đây không phải bằng chứng hệ thống không còn lỗi và không đại diện cho thử tải hay kiểm toán bảo mật.

### 9. Phân biệt kiểm thử đơn vị và API?

Unit test gọi trực tiếp hàm băm/kiểm tra mật khẩu và overdue_days. API test dùng TestClient đi qua định tuyến, kiểm tra đầu vào, xác thực và CSDL tạm. Ca tích hợp đồng thời gọi LoanService với hai luồng và kiểm tra số dòng cuối cùng. Test giao diện chạy server thật trong thread, mở Chromium headless, bấm nút và đọc DOM như người dùng — ví dụ nhập tiêu đề chứa thẻ `<img onerror>` để chứng minh không bị XSS.

### 10. Mật khẩu và phiên đăng nhập lưu ở đâu?

Mật khẩu lưu PBKDF2-HMAC-SHA256 260.000 vòng với salt ngẫu nhiên, không lưu bản rõ. Phiên không lưu server: cookie HttpOnly chứa token `user_id.hạn.dấu_vết_mật_khẩu.chữ_ký` ký bằng HMAC-SHA256 với khóa LIBRARY_SECRET; server kiểm tra chữ ký, hạn 8 giờ, tài khoản còn hoạt động và dấu vết mật khẩu. Nhờ vậy đổi mật khẩu hoặc ngừng tài khoản là phiên cũ hết hiệu lực, và nhiều instance (như trên Vercel) đều xác minh được. Sai mật khẩu 5 lần trong 15 phút bị khóa tạm. Cookie SameSite strict và custom header bảo vệ yêu cầu ghi trên cùng origin.

### 11. Vì sao độc giả không đăng nhập?

Đề bài chính yêu cầu quản lý độc giả, chưa bắt buộc cổng tự phục vụ. Độc giả là đối tượng nghiệp vụ, thủ thư thao tác thay. Nếu phát triển thêm, tạo tài khoản độc giả và phân quyền xem phiếu của chính mình.

### 12. Quy tắc 5 bản và 30 ngày từ đâu?

Đó là giả định nghiệp vụ nhóm chọn cho bản triển khai vì đề gốc chỉ nêu quản lý sách, độc giả, mượn/trả. Nhóm ghi rõ trong báo cáo để giảng viên kiểm tra và có thể sửa theo quy định thư viện thực tế.

### 13. Dữ liệu có thật không?

Độc giả và số điện thoại là dữ liệu giả lập. Một số tên sách là ví dụ quen thuộc; danh mục không phải dữ liệu thư mục chuẩn hóa. Danh sách thành viên bìa lấy từ thông tin nhóm cung cấp.

### 14. Chức năng chưa có là gì?

Chưa quản lý mã riêng từng bản vật lý (chỉ có ISBN theo đầu sách), phạt tiền, đặt trước, khôi phục hồ sơ đã lưu trữ hay phục hồi sao lưu bằng giao diện, HTTPS tự cấu hình. Chưa xác nhận tải lớn hay hoạt động 24/7; bản Vercel chỉ là demo không lưu dữ liệu bền. Bản hiện tại hoàn thành các luồng chính cộng gia hạn, quản lý tài khoản, tải danh sách về máy, sao lưu và phân trang ở quy mô thư viện nhỏ.

### 15. Giai đoạn phân tích khác thiết kế ra sao?

Phân tích mô tả khái niệm Sách, Độc giả, Phiếu mượn và tương tác nghiệp vụ. Thiết kế chỉ rõ DTO Pydantic, LoanService, module main/db/security, route HTTP, khóa ngoại và giao dịch, cùng cấu trúc ES modules của frontend. Các mô hình được đối chiếu với code, không mặc định mọi lớp khái niệm đều là Python class.

### 16. Gia hạn theo quy tắc nào, sao không cho gia hạn phiếu quá hạn?

Chỉ phiếu chưa trả, chưa quá hạn, chưa gia hạn lần nào; thêm 1–30 ngày tính từ hạn hiện tại, tối đa một lần. Phiếu đã quá hạn phải trả sách trước để tránh "hợp thức hóa" việc trễ hạn; đó là giả định nghiệp vụ của nhóm và có thể đổi theo quy định thư viện.

### 17. Vì sao frontend không dùng React/Vue?

Yêu cầu bản nộp là chạy bằng một cú đúp `start.bat`, không cài Node. JavaScript thuần chia ES modules, mỗi màn hình một file HTML + một file JS, HTML tạo bằng tagged template tự thoát ký tự nên vẫn an toàn và chia việc được cho bốn người. Nhóm dùng Prettier, ESLint và TypeScript kiểm tra kiểu trên file .js ở máy dev; nếu tiếp tục dự án thì có thể chuyển sang Vue với cùng cấu trúc trang.

### 18. Deploy lên Vercel thì dữ liệu ở đâu?

Vercel là serverless, đĩa chỉ đọc; app chép `library.db` ra `/tmp` của từng instance nên dữ liệu thêm/sửa chỉ sống trong instance đó và reset khi khởi động lạnh. Nhóm coi đó là bản demo để xem giao diện; dùng thật cần máy chủ có đĩa (VPS, Fly.io volume) hoặc đổi sang CSDL dịch vụ. Phiên đăng nhập đã làm stateless (token ký HMAC) nên không bị văng khi đổi instance.

## Các điểm cần kiểm tra trước khi nộp

- Bốn tên, mã sinh viên và lớp đúng danh sách nhóm.
- Bìa và bố cục theo mẫu Học viện: bìa BÁO CÁO ĐỒ ÁN MÔN HỌC (GVHD Nguyễn Thị Bích Nguyên, trưởng nhóm Lê Ngọc Khôi, TP.HCM tháng 10/2026), sau đó MỤC LỤC, DANH SÁCH HÌNH BẢNG, DANH MỤC TỪ VIẾT TẮT, Chương I–VI và TÀI LIỆU THAM KHẢO.
- Nội dung gốc là `docs/Bao_cao_Nhom_1.md`; DOCX/PDF được dựng lại từ file này. Nếu sửa trực tiếp trong Word, bấm Ctrl+A rồi F9 để cập nhật số trang mục lục trước khi xuất PDF.
- Nhóm đọc và chạy ít nhất một vòng demo, hiểu quy tắc và giới hạn đã ghi.
- Gửi cả source, database mẫu, báo cáo và test results. Không gửi `.venv`, `node_modules`, `data/backups`.
