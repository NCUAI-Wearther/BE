from dataclasses import dataclass

@dataclass
class LikeAddDTO:
    users_id: int
    posts_id: int

    @staticmethod
    def from_dict(data: dict) -> "LikeAddDTO":
        return LikeAddDTO(
            users_id=data.get('users_id'),
            posts_id=data.get('posts_id'),
        )