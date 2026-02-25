import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from routes import auth_route, view_route
from DB.database import engine
from models.user_model import Base
from fastapi.staticfiles import StaticFiles

#  KHỞI TẠO DATABASE
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Đang khởi tạo Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(" Database đã sẵn sàng!")
    yield
    print(" Server đang tắt...")

#  KHỞI TẠO APP FASTAPI
app = FastAPI(title="Messenger Web API", lifespan=lifespan)

#  KẾT NỐI FILE TĨNH (CSS, JS, IMAGES)

# app.mount("/static", StaticFiles(directory="static"), name="static")


#  KẾT NỐI CÁC ROUTER (API)
app.include_router(auth_route.router)
app.include_router(view_route.router)
# app.include_router(ws_route.router)


#  MIDDLEWARE (ĐO THỜI GIAN XỬ LÝ)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f" API {request.url.path} xử lý mất: {process_time:.4f}s")
    return response

#  BẮT LỖI TOÀN CỤC
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f" LỖI HỆ THỐNG: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Đã xảy ra lỗi hệ thống!",
            "detail": str(exc)
        }
    )