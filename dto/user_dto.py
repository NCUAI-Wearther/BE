from dataclasses import dataclass
import datetime
from typing import Optional
from sqlalchemy import TEXT

from models import Favorite, Like, Post,User

@dataclass
class UserRegisterDTO:
    username: str
    email: str
    password: str
    gender: Optional[str] = None
    birthday: Optional[datetime.date] = None

    @staticmethod
    def from_dict(data: dict) -> "UserRegisterDTO":
        return UserRegisterDTO(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            gender=data.get('gender'),
            birthday=data.get('birthday')
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
class LikeViewDTO:
    users_id: int
    outfits_id: int
    created_at: datetime

    @staticmethod
    def from_model(like: Like) -> "LikeViewDTO":
        return LikeViewDTO(
            users_id=like.users_id,
            outfits_id=like.outfits_id,
            created_at=like.created_at
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