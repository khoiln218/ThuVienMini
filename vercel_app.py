"""Điểm vào cho Vercel (khai báo trong pyproject.toml: [tool.vercel] entrypoint = "vercel_app:app").

Trên Vercel không có đĩa ghi bền vững: app/db.py thấy biến VERCEL=1 sẽ chép data/library.db ra /tmp và dùng ở đó,
nên bản này là CHẾ ĐỘ DEMO — dữ liệu thêm/sửa chỉ tồn tại trong instance hiện tại. Xem README mục "Triển khai lên Internet".

Đặt biến môi trường LIBRARY_VERCEL_DEMO=1 nếu muốn mỗi instance tự sinh lại dữ liệu demo (ngày mượn tính theo hôm nay)
thay vì chép data/library.db. Bộ demo là xác định (cả salt mật khẩu) nên các instance vẫn dùng chung phiên.
"""
import os
from datetime import date

from app.db import db_path

if os.environ.get('LIBRARY_VERCEL_DEMO') == '1' and os.environ.get('VERCEL'):
    target = db_path()
    if target.exists() and target.stat().st_size and not os.environ.get('_LIBRARY_DEMO_READY'):
        from seed import seed_demo
        target.unlink()
        seed_demo(target, date.today())
        os.environ['_LIBRARY_DEMO_READY'] = '1'

from app.main import app  # noqa: E402  Vercel nạp biến `app` (ASGI)
