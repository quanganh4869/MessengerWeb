from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Khởi tạo Base class cho tất cả các model
Base = declarative_base()

#  NGƯỜI DÙNG & MỐI QUAN HỆ

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Thiết lập mối quan hệ (Relationships)
    status = relationship("UserStatus", back_populates="user", uselist=False)
    participations = relationship("Participant", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    notifications = relationship("Notification", back_populates="user")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Người gửi lời mời
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Người nhận lời mời
    status = Column(String(20), default="pending") # Trạng thái: pending, accepted
    created_at = Column(DateTime, default=datetime.utcnow)

class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_online = Column(Boolean, default=False)
    last_active = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="status")

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================
# NHÓM 2: PHÒNG CHAT & TIN NHẮN
# ==========================================

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    is_group = Column(Boolean, default=False)
    name = Column(String(100), nullable=True) # Chỉ dùng nếu là chat nhóm
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship("Participant", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member") # admin, member
    joined_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User", back_populates="participations")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True) # Text có thể rỗng nếu tin nhắn chỉ chứa ảnh/file
    type = Column(String(20), default="text") # text, image, file
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message")
    reads = relationship("MessageRead", back_populates="message")


# ==========================================
# NHÓM 3: TÍNH NĂNG MỞ RỘNG (FILE, ĐÃ XEM, THÔNG BÁO)
# ==========================================

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True) # jpg, pdf, docx...
    file_size = Column(Integer, nullable=True) # Kích thước tính bằng byte

    message = relationship("Message", back_populates="attachments")

class MessageRead(Base):
    __tablename__ = "message_reads"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Ai là người đã đọc?
    read_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="reads")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")