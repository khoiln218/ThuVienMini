# Kịch bản trình bày báo cáo — Nhóm 1, đề tài Quản lý thư viện

Tổng thời lượng: **12 phút**, mỗi thành viên **3 phút**, theo bảng phân công trong `KICH_BAN_BAO_VE.md`. Lời thoại mỗi người khoảng 400–450 âm tiết, đọc ở tốc độ trình bày bình thường là vừa 3 phút. Cột "Màn hình" cho biết lúc đó chiếu gì; số hình/bảng theo bản PDF `Bao_cao_Nhom_1_Thu_vien.pdf`.

| Thứ tự | Thành viên | Nội dung | Thời lượng | Mốc kết thúc |
|---|---|---|---|---|
| 1 | Phạm Tuấn Anh | Bài toán, mục tiêu, phạm vi, quy trình nghiệp vụ, yêu cầu, use case (Chương I, II, III.I) | 3 phút | 03:00 |
| 2 | Phạm Phước Hòa | Sơ đồ hoạt động, mô hình dữ liệu, giao diện, xử lý (Chương III.II–V) | 3 phút | 06:00 |
| 3 | Lê Ngọc Khôi | Demo phần mềm (Chương IV) | 3 phút | 09:00 |
| 4 | Lê Bá Quảng | Cài đặt, thử nghiệm, kết luận, hạn chế, hướng phát triển (Chương V, VI) | 3 phút | 12:00 |

## Chuẩn bị trước buổi trình bày (không tính giờ)

- Máy chiếu mở sẵn hai cửa sổ: bản PDF báo cáo và trình duyệt tại `http://127.0.0.1:8000`, **đã đăng nhập `admin / Admin@123`** ở trang Tổng quan.
- Chạy `python seed.py --force` trước buổi để dữ liệu sạch và ngày mượn tính theo hôm nay.
- Chưa tạo sách `BV001` và độc giả `BV001` (Khôi tạo trực tiếp khi demo). Nếu phải demo lại trên cùng dữ liệu thì dùng mã `BV002`.
- Người kế tiếp đứng sẵn cạnh máy khi người trước còn khoảng 15 giây; câu chuyển lượt in nghiêng ở cuối mỗi phần.
- Người giữ giờ (người chưa nói) giơ tay khi còn 30 giây.

---

## 1. Phạm Tuấn Anh — Bài toán và yêu cầu (00:00 – 03:00)

| Thời điểm | Màn hình | Lời thoại |
|---|---|---|
| 00:00 | Trang bìa | Kính chào cô và các bạn. Nhóm 1 xin trình bày đề tài Quản lý thư viện, môn Nhập môn Công nghệ Phần mềm. Nhóm gồm bốn thành viên: em là Phạm Tuấn Anh, cùng các bạn Phạm Phước Hòa, Lê Ngọc Khôi và Lê Bá Quảng. Em xin trình bày phần bài toán và yêu cầu. |
| 00:20 | Chương I – Bảng 1.3 Vấn đề nghiệp vụ hiện tại | Thư viện nhóm khảo sát là một thư viện nhỏ, vài trăm đầu sách, một người phụ trách và một đến hai thủ thư. Hiện mọi việc đều ghi sổ tay. Vì vậy thủ thư không biết chính xác một cuốn còn bao nhiêu bản trên giá, một lần mượn nhiều cuốn bị ghi thành nhiều dòng rời nên trả một phần rất dễ nhầm, và muốn biết ai quá hạn thì phải lật cả cuốn sổ. |
| 00:50 | Bảng 1.1 Mục tiêu nghiệp vụ | Từ đó nhóm đặt ra năm mục tiêu: biết ngay số bản còn trên giá; mỗi lần mượn có đúng một phiếu, in ra được để độc giả ký; theo dõi được sách quá hạn; giữ trọn lịch sử mượn trả; và mỗi nhân viên có tài khoản riêng để phân định trách nhiệm. |
| 01:10 | Bảng 1.4 So sánh AS-IS / TO-BE | Bảng này so sánh cách làm cũ và quy trình đề xuất. Điểm thay đổi quan trọng nhất là: mỗi lần mượn lập một phiếu gồm tất cả các cuốn, phần mềm kiểm tra giới hạn trước khi cho mượn, và khi trả thì đánh dấu theo từng cuốn. |
| 01:30 | Chương II – mục I, II, III | Chương hai mô tả ba quy trình nghiệp vụ: mượn sách, trả sách và gia hạn phiếu. Khi mượn, một phiếu có từ một đến năm cuốn, mỗi độc giả giữ tối đa năm cuốn, và cuốn nào hết bản thì không cho mượn. Khi trả, độc giả có thể trả từng cuốn; phiếu chỉ hoàn tất khi đã trả đủ. Phiếu còn trong hạn được gia hạn đúng một lần. |
| 02:00 | Bảng 2.2 Chức năng của Thủ thư | Yêu cầu được ghi theo mẫu của bộ môn: mỗi công việc một dòng, kèm loại công việc, quy định và biểu mẫu. Phần mềm có hai đối tượng sử dụng là thủ thư và quản trị viên; quản trị viên có thêm quyền lưu trữ hồ sơ, quản lý tài khoản và sao lưu. |
| 02:20 | Chương III – Hình 3.1 đến 3.4, Bảng 3.1 | Từ các yêu cầu đó, nhóm xác định mười ba use case chính, chia ba nhóm: quản lý sách, quản lý độc giả và mượn trả, cộng với đăng nhập. Theo góp ý của cô, mỗi thao tác thêm, sửa, tìm kiếm, lưu trữ là một use case riêng, không gộp thành "quản lý". Mỗi use case đều có bảng đặc tả với luồng chính và các ngoại lệ. |
| 02:50 | | *Phần tiếp theo, bạn Phước Hòa sẽ trình bày sơ đồ hoạt động và thiết kế dữ liệu.* |

## 2. Phạm Phước Hòa — Phân tích thiết kế (03:00 – 06:00)

| Thời điểm | Màn hình | Lời thoại |
|---|---|---|
| 03:00 | Mục III.II – Hình 3.5 Đăng nhập | Em là Phạm Phước Hòa. Em xin trình bày phần phân tích thiết kế. Nhóm vẽ sơ đồ hoạt động cho bốn luồng tiêu biểu. Mỗi sơ đồ chia hai làn, người dùng và hệ thống, và mọi nhánh, kể cả nhánh bị từ chối, đều kết thúc bằng bước hiển thị kết quả cho người dùng. |
| 03:25 | Hình 3.7 Lập phiếu mượn | Đây là luồng quan trọng nhất, lập phiếu mượn. Thủ thư chọn độc giả, đánh dấu các cuốn và nhập số ngày. Hệ thống kiểm tra lần lượt bốn điều kiện: dữ liệu hợp lệ, độc giả và sách còn sử dụng, tổng số cuốn không quá năm, và cuốn nào cũng còn bản. Chỉ khi đạt cả bốn thì mới lập phiếu và ghi chi tiết cho tất cả các cuốn cùng lúc, nên không bao giờ có phiếu thiếu cuốn. |
| 04:00 | Hình 3.8 Trả sách | Với trả sách, thủ thư bỏ chọn những cuốn độc giả chưa mang tới. Kết quả hiển thị khác nhau: còn thiếu mấy cuốn, hoặc phiếu đã trả đủ. |
| 04:20 | Mục III.III – Hình 3.9 ERD | Về dữ liệu, nhóm vẽ lại ERD theo đúng ký pháp Chen. Có năm thực thể: người dùng, độc giả, sách, phiếu mượn và chi tiết phiếu mượn. Phiếu mượn và sách có quan hệ nhiều – nhiều, lại có thông tin riêng là ngày trả từng cuốn, nên được tách thành thực thể yếu "chi tiết phiếu mượn", vẽ viền đôi. Số bản có sẵn là thuộc tính dẫn xuất, vẽ nét đứt, vì nó được tính bằng tổng số bản trừ số cuốn chưa trả. |
| 05:00 | Hình 3.10 và Bảng 3.16 | Từ ERD, mỗi thực thể thành một bảng dữ liệu. Bảng người dùng đã bổ sung họ tên, email và điện thoại theo góp ý của cô. Các trạng thái như số bản có sẵn, phiếu đang mượn hay quá hạn không lưu thành cột mà tính lại mỗi lần xem, nên luôn khớp với dữ liệu gốc. |
| 05:25 | Mục III.IV – Hình 3.14 Wireframe Lập phiếu mượn | Về giao diện, các màn hình danh sách dùng chung một bố cục. Hộp thoại lập phiếu cho đánh dấu nhiều cuốn, có ô lọc và bộ đếm số cuốn đã chọn. Mục thiết kế xử lý mô tả thêm cách phần mềm xử lý khi hai thủ thư cùng cho mượn bản cuối cùng: chỉ người thao tác trước thành công. |
| 05:50 | | *Sau đây bạn Khôi sẽ demo trực tiếp phần mềm.* |

## 3. Lê Ngọc Khôi — Demo phần mềm (06:00 – 09:00)

Lời thoại ngắn, vừa nói vừa thao tác. Nếu chậm hơn mốc giờ, bỏ bước 7 (gia hạn).

| Thời điểm | Thao tác trên trình duyệt | Lời thoại |
|---|---|---|
| 06:00 | Trang Tổng quan (đã đăng nhập admin) | Em là Lê Ngọc Khôi, em xin demo phần mềm. Đây là trang tổng quan: số đầu sách, số bản có sẵn, số bản đang mượn và danh sách phiếu quá hạn cần nhắc. |
| 06:15 | Kho sách → "+ Thêm sách": mã `BV001`, tên `Sách bảo vệ`, tác giả `Nhóm 1`, thể loại `Tin học`, tổng bản `1` → Lưu | Em thêm một đầu sách mới chỉ có một bản. Sau khi lưu, phần mềm báo "Đã lưu" và sách hiện trong kho với một bản có sẵn. |
| 06:35 | "+ Thêm sách" lần nữa với mã `BV001` → Lưu | Nếu nhập trùng mã, phần mềm báo mã đã tồn tại và giữ nguyên dữ liệu đang nhập. Em bấm Hủy. |
| 06:45 | Độc giả → "+ Thêm độc giả": mã `BV001`, họ tên `Độc giả demo` → Lưu | Thêm một độc giả mới. |
| 07:00 | Mượn & trả → "+ Lập phiếu mượn": chọn `BV001 · Độc giả demo`; ô lọc gõ `BV001`, đánh dấu; gõ `Cơ sở dữ liệu`, đánh dấu; giữ ô "In phiếu ngay sau khi lập" → Lập phiếu | Bây giờ là nghiệp vụ chính. Một lần mượn lập một phiếu: em chọn độc giả, đánh dấu hai cuốn, bộ đếm hiện "đã chọn 2". Bấm Lập phiếu. |
| 07:25 | Hộp thoại in hiện ra → chỉ vào phiếu → Hủy | Phần mềm báo "Đã lập phiếu mượn gồm 2 cuốn" và mở ngay phiếu in, có danh sách sách, hạn trả và chỗ ký của độc giả và thủ thư. Em hủy in để tiếp tục. |
| 07:45 | Kho sách → nút "Lưu trữ" ở `BV001` → OK | Sách BV001 giờ còn 0 bản. Nếu em thử lưu trữ sách đang được mượn, phần mềm từ chối: "Còn sách chưa trả, không thể lưu trữ". |
| 08:05 | Mượn & trả → phiếu vừa lập → "Trả sách": bỏ chọn `Cơ sở dữ liệu` → Xác nhận đã nhận sách | Độc giả mang trả một cuốn. Em bỏ chọn cuốn chưa mang tới. Phần mềm báo "phiếu còn 1 cuốn chưa trả", cuốn đã trả hiện mờ kèm ngày trả. |
| 08:25 | "Trả sách" lần nữa → Xác nhận | Trả nốt cuốn còn lại: "phiếu đã trả đủ", phiếu chuyển trạng thái Đã trả và vẫn nằm trong lịch sử. |
| 08:40 | (Bước 7, có thể bỏ) Lọc "Đang mượn trong hạn" → "Gia hạn" một phiếu → 7 ngày → Gia hạn | Phiếu còn trong hạn được gia hạn một lần; sau khi gia hạn, nút Gia hạn biến mất. |
| 08:50 | | *Phần cuối, bạn Quảng sẽ trình bày kết quả cài đặt, thử nghiệm và kết luận.* |

## 4. Lê Bá Quảng — Triển khai và kết luận (09:00 – 12:00)

| Thời điểm | Màn hình | Lời thoại |
|---|---|---|
| 09:00 | Chương V – Bảng 5.1 Tình trạng cài đặt | Em là Lê Bá Quảng. Em xin trình bày phần triển khai và kết luận. Bảng này liệt kê mười bốn chức năng đã cài đặt, tất cả đều hoàn thành một trăm phần trăm, từ đăng nhập, quản lý sách, độc giả, lập và in phiếu mượn, trả sách, gia hạn, cho tới quản lý tài khoản và sao lưu dữ liệu. |
| 09:25 | Mục V.II Thử nghiệm | Phần mềm cài trên một máy tính thông thường, khởi động bằng một lần nhấp, không cần Internet và không tốn phí. Nhóm chuẩn bị tài khoản thử nghiệm cho hai đối tượng: quản trị viên là admin, thủ thư là thuthu. Đăng nhập bằng tài khoản thủ thư sẽ không thấy các chức năng lưu trữ, tài khoản và sao lưu. |
| 09:50 | (Có thể mở `docs/ket_qua_kiem_thu.csv`) | Ngoài thử tay, nhóm viết bộ kiểm thử tự động gồm tám mươi lần chạy, kiểm tra các quy tắc như giới hạn năm cuốn, trả trùng, gia hạn hai lần, hai thủ thư cùng cho mượn bản cuối cùng, và mười kịch bản chạy trên trình duyệt thật. Tất cả đều đạt. |
| 10:20 | Chương VI – mục I | Tóm lại, nhóm đã hoàn thành ba nghiệp vụ chính của đề tài là quản lý sách, quản lý độc giả và mượn trả. Mô hình dữ liệu bám đúng chứng từ thực tế: một phiếu mượn với nhiều dòng chi tiết. Báo cáo được viết lại theo đúng mẫu của bộ môn và theo các góp ý của cô ở buổi trước. |
| 10:50 | Mục VI.II Ưu khuyết điểm | Về ưu điểm, số liệu luôn khớp vì số bản có sẵn được tính từ các phiếu chưa trả, mọi thao tác đều báo kết quả rõ ràng, và phiếu mượn in được ngay từ phần mềm. Về hạn chế, nhóm chưa quản lý riêng từng bản sách, chưa tính tiền phạt, chưa có trang cho độc giả tự tra cứu, và hồ sơ đã lưu trữ chưa xem lại được trên giao diện. |
| 11:25 | Mục VI.III Hướng mở rộng | Hướng phát triển tiếp theo là gắn mã riêng cho từng cuốn, cho phép khôi phục hồ sơ đã lưu trữ, tính tiền phạt, đặt trước sách và gửi tin nhắn nhắc hạn trả. |
| 11:45 | Trang cuối | Phần trình bày của nhóm đến đây là kết thúc. Nhóm em cảm ơn cô và các bạn đã lắng nghe, và rất mong nhận được góp ý của cô. |

---

## Phương án dự phòng

- **Máy demo lỗi:** Khôi chuyển sang trình bày bằng ảnh màn hình trong Chương IV của PDF (Hình 4.6 lập phiếu, 4.8 phiếu in, 4.9–4.10 trả một phần) theo đúng thứ tự trên, vẫn giữ 3 phút.
- **Bị hỏi xen giữa:** trả lời ngắn rồi tiếp tục; câu hỏi dài để phần hỏi đáp cuối. Câu trả lời mẫu nằm ở mục "Câu hỏi dự kiến" trong `KICH_BAN_BAO_VE.md`.
- **Quá giờ:** Tuấn Anh bỏ đoạn 02:00 (bảng chức năng); Hòa bỏ đoạn 05:25 (giao diện); Khôi bỏ bước gia hạn; Quảng rút gọn đoạn 11:25 (hướng mở rộng) thành một câu.
