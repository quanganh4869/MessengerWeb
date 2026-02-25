import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

#  Lấy URL Database chuẩn PostgreSQL Async
DATABASE_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:123456@localhost:5432/webchat_db")

#  Tạo Engine Bất đồng bộ (Đã xóa check_same_thread của SQLite)
engine = create_async_engine(
    DATABASE_URL,
    echo=False, # Đổi thành True nếu bạn muốn xem câu lệnh SQL
)

#  Tạo Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 5. Dependency cấp phát Session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()