import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

def hash_password(password, salt=None):
    """PBKDF2-HMAC-SHA256 với salt ngẫu nhiên. `salt` chỉ truyền khi cần kết quả lặp lại (dữ liệu demo sinh trên
    nhiều instance phải giống hệt nhau); tài khoản thật luôn để None."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000).hex()
    return f'{salt}${digest}'

def verify_password(password, stored):
    salt, digest = stored.split('$')
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000).hex()
    return hmac.compare_digest(actual, digest)

SESSION_SECONDS = 8 * 3600
_secret = None


def get_secret():
    """Khóa ký phiên. Ưu tiên biến môi trường LIBRARY_SECRET (bắt buộc khi chạy nhiều instance như Vercel);
    tại máy thì tự sinh một lần và lưu vào data/.secret để khởi động lại không phải đăng nhập lại."""
    global _secret
    if _secret:
        return _secret
    if os.environ.get('LIBRARY_SECRET'):
        _secret = os.environ['LIBRARY_SECRET'].encode()
        return _secret
    path = Path(__file__).resolve().parent.parent / 'data' / '.secret'
    try:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(secrets.token_hex(32))
        _secret = path.read_text().strip().encode()
    except OSError:
        # Đĩa chỉ đọc (serverless) mà không đặt LIBRARY_SECRET. Nếu tự sinh ngẫu nhiên thì mỗi instance một khóa và
        # phiên chỉ hợp lệ trên instance đã đăng nhập → người dùng bị văng ra. Dự phòng: suy khóa từ định danh
        # deployment (giống nhau trên mọi instance của cùng bản deploy). Không bí mật bằng LIBRARY_SECRET nên chỉ
        # phù hợp bản demo; README yêu cầu đặt LIBRARY_SECRET khi triển khai.
        anchor = os.environ.get('VERCEL_DEPLOYMENT_ID') or os.environ.get('VERCEL_GIT_COMMIT_SHA') or os.environ.get('VERCEL_URL')
        if anchor:
            print('CẢNH BÁO: chưa đặt LIBRARY_SECRET; đang dùng khóa suy từ deployment. Đặt LIBRARY_SECRET trong Environment Variables rồi redeploy.')
            _secret = hashlib.sha256(f'thuvienmini:{anchor}'.encode()).digest()
        else:
            print('CẢNH BÁO: không lưu được data/.secret; đặt biến môi trường LIBRARY_SECRET để phiên đăng nhập ổn định.')
            _secret = secrets.token_bytes(32)
    return _secret


def password_fingerprint(password_hash):
    """Dấu vết của mật khẩu hiện tại gắn vào token: đổi mật khẩu thì mọi phiên cũ tự hết hạn."""
    return hashlib.sha256(password_hash.encode()).hexdigest()[:16]


def _sign(payload):
    return hmac.new(get_secret(), payload.encode(), 'sha256').hexdigest()[:32]


def make_token(user_id, password_hash, expires_at=None):
    """Token phiên không lưu server (stateless): user_id.hạn.dấu_vết_mật_khẩu.chữ_ký."""
    payload = f"{user_id}.{expires_at if expires_at is not None else int(time.time()) + SESSION_SECONDS}.{password_fingerprint(password_hash)}"
    return f'{payload}.{_sign(payload)}'


def parse_token(token):
    """Trả về (user_id, fingerprint) nếu chữ ký đúng và chưa hết hạn, ngược lại None."""
    try:
        user_id, expires_at, fingerprint, signature = token.split('.')
        payload = f'{user_id}.{expires_at}.{fingerprint}'
        if not hmac.compare_digest(_sign(payload), signature) or int(expires_at) <= time.time():
            return None
        return int(user_id), fingerprint
    except (ValueError, AttributeError):
        return None

class LoginGuard:
    """Chống dò mật khẩu: khóa tạm một cặp (tài khoản, địa chỉ) sau nhiều lần sai liên tiếp. Lưu trong bộ nhớ, đủ cho một máy chủ."""
    def __init__(self, limit=5, window=900):
        self.limit, self.window, self.failures = limit, window, {}

    def check(self, key):
        failures = [t for t in self.failures.get(key, []) if t > time.time() - self.window]
        self.failures[key] = failures
        if len(failures) >= self.limit:
            return int(failures[0] + self.window - time.time())
        return 0

    def fail(self, key):
        self.failures.setdefault(key, []).append(time.time())

    def succeed(self, key):
        self.failures.pop(key, None)

    def reset(self):
        self.failures.clear()
