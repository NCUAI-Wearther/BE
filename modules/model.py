from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from typing import Optional,Dict, Any
from datetime import datetime

# 使用者
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=200)
    email: EmailStr

class UserCreate(UserBase):
    profile_pic_url: Optional[str] = None
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    profile_pic_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 天氣
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

    @field_validator('longitude')
    @classmethod
    def longitude_must_be_valid(cls, v):
        if not -180.0 <= v <= 180.0:
            raise ValueError('longitude must be between -180 and 180')
        return v

    @field_validator('latitude')
    @classmethod
    def latitude_must_be_valid(cls, v):
        if not -90.0 <= v <= 90.0:
            raise ValueError('latitude must be between -90 and 90')
        return v

class WeatherResponse(BaseModel):
    message: str
    data: Dict[str, Any]

class ForecastResponse(BaseModel):
    message: str
    data: Dict[str, Any]

# 穿著
class OutfitBase(BaseModel):
    outfits: str = Field(..., max_length=45)

class OutfitCreate(OutfitBase):
    pass

class OutfitResponse(OutfitBase):
    id: int

    class Config:
        from_attributes = True
        
# 貼文
class PostBase(BaseModel):
    user_id: int
    outfits_id: int
    content: str
    media_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 點讚
class LikeBase(BaseModel):
    user_id: int
    post_id: int

class LikeCreate(LikeBase):
    pass

class LikeResponse(LikeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    user_id: int
    outfits_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 通用
class MessageResponse(BaseModel):
    message: str
    
class DetailedResponse(MessageResponse):
    details: Optional[Dict[str, Any]] = None