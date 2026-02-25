import sys
import os

# Thêm thư mục gốc (chứa main.py) vào tầm nhìn của Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app # Bây giờ dòng này sẽ hoạt động hoàn hảo!
from DB.database import get_db
from models.user_model import Base
# ... (phần code còn lại giữ nguyên) ...
# ================= 1. SETUP DATABASE ẢO =================
# Dùng SQLite ảo trong RAM để test cực nhanh và không ảnh hưởng DB thật
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

# Hàm ghi đè (Override)
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Bảo FastAPI: "Mỗi khi API cần get_db, hãy dùng override_get_db nhé!"
app.dependency_overrides[get_db] = override_get_db

# ================= 2. FIXTURES =================
# Chạy trước MỖI test case: Tạo bảng. Chạy xong: Xóa bảng.
@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Tạo Client giả lập (như Postman/Swagger) để gọi API
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# ================= 3. CÁC KỊCH BẢN TEST (TEST CASES) =================

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Test kịch bản Đăng ký thành công"""
    response = await async_client.post(
        "/auth/register",
        json={"email": "test@gmail.com", "password": "mypassword123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@gmail.com"
    assert "hashed_password" not in data # Đảm bảo không lộ password ra ngoài

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    """Test kịch bản Đăng ký trùng Email"""
    # 1. Tạo user lần đầu
    await async_client.post(
        "/auth/register",
        json={"email": "test@gmail.com", "password": "mypassword123"}
    )
    # 2. Cố tình tạo lại y hệt
    response = await async_client.post(
        "/auth/register",
        json={"email": "test@gmail.com", "password": "newpassword456"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email đã được sử dụng"

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """Test kịch bản Đăng nhập thành công và Lấy Token"""
    # 1. Phải đăng ký trước
    await async_client.post(
        "/auth/register",
        json={"email": "test@gmail.com", "password": "mypassword123"}
    )
    # 2. Đăng nhập (Lưu ý: Login dùng form-urlencoded, không dùng json)
    response = await async_client.post(
        "/auth/login",
        data={"username": "test@gmail.com", "password": "mypassword123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_me_unauthorized(async_client: AsyncClient):
    """Test kịch bản vào API bảo mật khi Không có Token (Bị anh bảo vệ đuổi)"""
    response = await async_client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"