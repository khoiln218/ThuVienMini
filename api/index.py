"""Điểm vào cho Vercel (Python Serverless Function, ASGI).

Vercel không có ổ đĩa ghi bền vững: chỉ /tmp ghi được và mất khi function khởi động lạnh.
Vì vậy bản trên Vercel là CHẾ ĐỘ DEMO: mỗi instance chép data/library.db (hoặc tự tạo demo lớn nếu
LIBRARY_VERCEL_DEMO=1) vào /tmp rồi chạy; dữ liệu thêm/sửa chỉ tồn tại trong instance đó.
Chạy thật cần máy chủ có đĩa (xem README, mục "Triển khai lên Internet").
"""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TMP_DB = Path('/tmp/thuvienmini/library.db')
os.environ.setdefault('LIBRARY_DB', str(TMP_DB))
os.environ.setdefault('LIBRARY_BACKUP', '0')   # không có chỗ lưu sao lưu trên Vercel

db = Path(os.environ['LIBRARY_DB'])
db.parent.mkdir(parents=True, exist_ok=True)
if not db.exists():
    if os.environ.get('LIBRARY_VERCEL_DEMO') == '1':
        from datetime import date
        from seed import seed_demo
        seed_demo(db, date.today())
    else:
        shutil.copy(ROOT / 'data/library.db', db)

from app.main import app  # noqa: E402  Vercel tìm biến `app` (ASGI)
