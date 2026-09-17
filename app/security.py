import hashlib
import hmac
import secrets
import time

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000).hex()
    return f'{salt}${digest}'

def verify_password(password, stored):
    salt, digest = stored.split('$')
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000).hex()
    return hmac.compare_digest(actual, digest)

def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

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
