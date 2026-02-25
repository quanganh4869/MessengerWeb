from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from DB.database import get_db
from core.config import ALGORITHM, SECRET_KEY, create_access_token, hash_password, verify_password
from models.user_model import User
from schemas.user_schema import UserCreate, UserOut



templates = Jinja2Templates(directory="Frontend/templates")
router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Hàm Gác cổng
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin (Token không hợp lệ hoặc đã hết hạn)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Lấy thông tin User từ Database
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user


@router.get("/welcome")
async def welcome():
    return {"message": "Chào mừng bạn đến với API Messenger!"}

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    print(f"Password thực tế server nhận được: '{user_in.password}'")
    print(f"Độ dài của password này là: {len(user_in.password)} ký tự")
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    user_exists = result.scalars().first()

    if user_exists:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Tìm user theo email
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Sai email hoặc mật khẩu")

    # Tạo Token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    API này yêu cầu phải có JWT Token hợp lệ mới xem được.
    """
    return current_user

@router.put("/me", response_model=UserOut)
async def update_my_profile(
    user_update: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin cá nhân của chính mình.
    Yêu cầu phải có JWT Token hợp lệ.
    """
    current_user.full_name = user_update.full_name or current_user.full_name
    if user_update.password:
        current_user.hashed_password = hash_password(user_update.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/users", response_model=List[UserOut])
async def get_all_users(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    API lấy danh sách tất cả người dùng để hiển thị lên sidebar.
    Không bao gồm user hiện tại đang đăng nhập.
    """
    # Tìm tất cả user có ID KHÁC với ID của người đang request
    stmt = select(User).where(User.id != current_user.id)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


@router.get("/users/all", response_model=List[UserOut])
async def get_all_users_including_current(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

