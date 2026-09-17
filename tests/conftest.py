import pytest
from fastapi.testclient import TestClient
from app.main import app
from seed import seed

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('LIBRARY_DB', str(tmp_path / 'test.db'))
    seed()
    with TestClient(app, headers={'X-Library-Request':'1'}) as client:
        assert client.post('/api/login', json={'username':'admin','password':'Admin@123'}).status_code == 200
        yield client

@pytest.fixture
def book():
    return {'code':'NEW','title':'Sách kiểm thử','author':'Tác giả','category':'Tin học','total':2}

@pytest.fixture
def reader():
    return {'code':'NEW','name':'Độc giả kiểm thử','phone':'0901234567'}
