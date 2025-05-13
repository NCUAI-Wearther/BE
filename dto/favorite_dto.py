from dataclasses import dataclass

@dataclass
class FavoriteAddDTO:
    users_id: int
    outfits_id: int

    @staticmethod
    def from_dict(data: dict) -> "FavoriteAddDTO":
        return FavoriteAddDTO(
            users_id=data.get('users_id'),
            outfits_id=data.get('outfits_id'),
        )