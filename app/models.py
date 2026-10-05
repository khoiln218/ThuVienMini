from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

PHONE = r'^[0-9+ ()-]*$'

class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

class Login(Input):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)

class Book(Input):
    code: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=60)
    total: int = Field(ge=0, le=999, strict=True)
    # Mã vạch/ISBN in trên sách (EAN-13 là 13 chữ số); không bắt buộc, duy nhất khi có
    barcode: str = Field(default='', max_length=20, pattern=r'^[0-9A-Za-z-]*$')

class Reader(Input):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(default='', max_length=20, pattern=PHONE)

ID = Annotated[int, Field(gt=0, strict=True)]
MAX_BORROWED = 5  # số bản tối đa một độc giả được giữ cùng lúc, cũng là số sách tối đa trên một phiếu

class Borrow(Input):
    reader_id: ID
    # Mỗi lần mượn lập một phiếu gồm một hoặc nhiều đầu sách, mỗi đầu sách một bản
    book_ids: list[ID] = Field(min_length=1, max_length=MAX_BORROWED)
    days: int = Field(default=14, ge=1, le=30, strict=True)

class Return(Input):
    # Bỏ trống: trả toàn bộ sách còn lại của phiếu; có giá trị: chỉ trả các dòng chi tiết này
    item_ids: list[ID] | None = Field(default=None, min_length=1)

class Extend(Input):
    days: int = Field(default=7, ge=1, le=30, strict=True)

PASSWORD = Field(min_length=8, max_length=128)
EMAIL = r'^([^@\s]+@[^@\s]+\.[^@\s]+)?$'

class UserCreate(Input):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[A-Za-z0-9._-]+$')
    password: str = PASSWORD
    role: str = Field(pattern=r'^(admin|librarian)$')
    full_name: str = Field(min_length=1, max_length=100)
    email: str = Field(default='', max_length=100, pattern=EMAIL)
    phone: str = Field(default='', max_length=20, pattern=PHONE)

class UserUpdate(Input):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=100, pattern=EMAIL)
    phone: str | None = Field(default=None, max_length=20, pattern=PHONE)
    role: str | None = Field(default=None, pattern=r'^(admin|librarian)$')
    active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

class PasswordChange(Input):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = PASSWORD
