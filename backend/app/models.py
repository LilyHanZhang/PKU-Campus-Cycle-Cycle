from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from .database import Base

class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class BicycleStatus(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    IN_STOCK = "IN_STOCK"
    LOCKED = "LOCKED"
    SOLD = "SOLD"

class AppointmentType(str, enum.Enum):
    DROP_OFF = "drop-off"
    PICK_UP = "pick-up"

class AppointmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    role = Column(String(20), default=Role.USER.value)
    avatar_url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    bicycles = relationship("Bicycle", back_populates="owner")
    appointments = relationship("Appointment", back_populates="user")
    posts = relationship("Post", back_populates="author")

class Bicycle(Base):
    __tablename__ = "bicycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    brand = Column(String(100), nullable=False)
    condition = Column(Integer)
    price = Column(Float, default=0)
    status = Column(String(20), default=BicycleStatus.PENDING_APPROVAL.value)
    image_url = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="bicycles")
    appointments = relationship("Appointment", back_populates="bicycle")
    time_slots = relationship("TimeSlot", back_populates="bicycle")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    bicycle_id = Column(UUID(as_uuid=True), ForeignKey("bicycles.id"))
    type = Column(String(20))
    status = Column(String(20), default=AppointmentStatus.PENDING.value)
    appointment_time = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="appointments")
    bicycle = relationship("Bicycle", back_populates="appointments")

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="comments")
    author = relationship("User")

class Like(Base):
    __tablename__ = "likes"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="likes")
    user = relationship("User")

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bicycle_id = Column(UUID(as_uuid=True), ForeignKey("bicycles.id"))
    appointment_type = Column(String(20))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(String(10), default="false")
    created_at = Column(DateTime, server_default=func.now())

    bicycle = relationship("Bicycle", back_populates="time_slots")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rating = Column(Integer)
    content = Column(Text)
    review_type = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    appointment = relationship("Appointment")
    reviewer = relationship("User")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
