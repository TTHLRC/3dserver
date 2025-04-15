from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import validator

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Position(BaseModel):
    x: float
    y: float
    z: float

class Cube(BaseModel):
    position: Position
    uuid: str

class ThreeDData(BaseModel):
    cubes: List[Cube]
    selectedCubes: List[str] = []
    hingePoints: List[Dict] = []

class UserData(BaseModel):
    id: int
    user_id: int
    content: ThreeDData
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        exclude_none = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Login(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @validator('username', 'email')
    def check_username_or_email(cls, v, values):
        if not v and not values.get('email' if v == 'username' else 'username'):
            raise ValueError('Either username or email must be provided')
        return v

class UpdateData(BaseModel):
    type: str
    content: str

    @validator('type')
    def validate_type(cls, v):
        if v not in ['initial', 'target', 'real_time']:
            raise ValueError('type must be one of: initial, target, real_time')
        return v 