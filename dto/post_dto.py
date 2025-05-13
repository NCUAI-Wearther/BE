from dataclasses import dataclass
import datetime
from typing import Optional
from sqlalchemy import TEXT

from models import Post

@dataclass
class PostCreateDTO:
    users_id: int
    outfits_id: int
    content: Optional[TEXT] = None
    media_url: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "PostCreateDTO":
        return PostCreateDTO(
            users_id=data.get('users_id'),
            outfits_id=data.get('outfits_id'),
            content=data.get('content'),
            media_url=data.get('media_url'),
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
class PostUpdateDTO:
    content: Optional[TEXT] = None
    media_url: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "PostUpdateDTO":
        return PostUpdateDTO(
            content=data.get('content'),
            media_url=data.get('media_url'),
        )
        