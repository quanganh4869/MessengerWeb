from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Views"])
templates = Jinja2Templates(directory="Frontend/templates")

@router.get("/home")
async def render_chat_home(request: Request):
    """
    Trang chủ của ứng dụng Chat (Giao diện chính)
    """
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse("log_regis.html", {"request": request})