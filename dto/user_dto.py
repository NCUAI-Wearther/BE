from dataclasses import dataclass
import datetime
from typing import Optional
from sqlalchemy import TEXT

from models import Favorite, Post, TryOn, User

@dataclass
class UserRegisterDTO:
    username: str
    email: str
    birthday: datetime.date
    password: str
    gender: Optional[str] = None
    profile_pic_url: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "UserRegisterDTO":
        return UserRegisterDTO(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            gender=data.get('gender'),
            birthday=data.get('birthday'),
            profile_pic_url=data.get('profile_pic_url')
        )

@dataclass
class UserLoginDTO:
    email: str
    password: str

    @staticmethod
    def from_dict(data: dict) -> "UserLoginDTO":
        return UserLoginDTO(
            email=data.get('email'),
            password=data.get('password'),
        )

@dataclass
class UserViewDTO:
    id: int
    username: str
    email: str
    created_at: datetime
    gender: Optional[str] = None
    birthday: Optional[datetime.date] = None
    profile_pic_url: Optional[str] = None

    @staticmethod
    def from_model(user: User) -> "UserViewDTO":
        return UserViewDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            gender=user.gender,
            birthday=user.birthday,
            profile_pic_url=user.profile_pic_url,
            created_at=user.created_at
        )

@dataclass
class UserUpdateDTO:
    username: str
    email: str
    password: str
    birthday: datetime.date
    gender: Optional[str] = None
    profile_pic_url: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "UserUpdateDTO":
        return UserUpdateDTO(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            gender=data.get('gender'),
            birthday=data.get('birthday'),
            profile_pic_url=data.get('profile_pic_url'),
        )
              
@dataclass
class FavoriteViewDTO:
    users_id: int
    outfits_id: int
    created_at: datetime

    @staticmethod
    def from_model(favorite: Favorite) -> "FavoriteViewDTO":
        return FavoriteViewDTO(
            users_id=favorite.users_id,
            outfits_id=favorite.outfits_id,
            created_at=favorite.created_at
        )
        
@dataclass
class PostViewDTO:
    id: int
    users_id: int
    outfits_id: int
    created_at: datetime
    content: Optional[TEXT] = None
    media_url: Optional[str] = None

    @staticmethod
    def from_model(post: Post) -> "PostViewDTO":
        return PostViewDTO(
            id=post.id,
            users_id=post.users_id,
            outfits_id=post.outfits_id,
            created_at=post.created_at
        )

@dataclass
class TryonViewDTO:
    users_id: int
    clothes_id: int
    category: str

    @staticmethod
    def from_dict(data: dict) -> "TryonViewDTO":
        return TryonViewDTO(
            users_id=data.get('users_id'),
            clothes_id=data.get('clothes_id'),
            category=data.get('category'),
        )
