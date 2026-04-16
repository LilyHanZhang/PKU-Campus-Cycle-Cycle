from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    role: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class BicycleBase(BaseModel):
    brand: str
    condition: int = Field(..., ge=1, le=10)
    price: float = 0
    description: Optional[str] = None
    image_url: Optional[str] = None

class BicycleCreate(BicycleBase):
    pass

class BicycleUpdate(BaseModel):
    brand: Optional[str] = None
    condition: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class BicycleResponse(BicycleBase):
    id: UUID
    owner_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    bicycle_id: UUID
    type: str = Field(..., pattern="^(drop-off|pick-up)$")
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: UUID
    post_id: UUID
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(USER|ADMIN|SUPER_ADMIN)$")
