from dataclasses import dataclass

@dataclass
class TryOnDTO:
    users_id: int
    clothes_id: int

    @staticmethod
    def from_dict(data: dict) -> "TryOnDTO":
        return TryOnDTO(
            users_id=data.get('users_id'),
            clothes_id=data.get('clothes_id'),
        )
