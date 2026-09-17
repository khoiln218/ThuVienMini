from pydantic import BaseModel, Field, ConfigDict

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

class Reader(Input):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(default='', max_length=20, pattern=r'^[0-9+ ()-]*$')

class Borrow(Input):
    book_id: int = Field(gt=0, strict=True)
    reader_id: int = Field(gt=0, strict=True)
    days: int = Field(default=14, ge=1, le=30, strict=True)

class Extend(Input):
    days: int = Field(default=7, ge=1, le=30, strict=True)

PASSWORD = Field(min_length=8, max_length=128)

class UserCreate(Input):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[A-Za-z0-9._-]+$')
    password: str = PASSWORD
    role: str = Field(pattern=r'^(admin|librarian)$')

class UserUpdate(Input):
    role: str | None = Field(default=None, pattern=r'^(admin|librarian)$')
    active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

class PasswordChange(Input):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = PASSWORD
