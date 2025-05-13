from dataclasses import dataclass
import datetime
from typing import Optional
from models import Outfit, OutfitItem

@dataclass
class OutfitCreateDTO:
    styleTag: str
    occasionTag: str
    name: str
    weather: str
    season:str
    img_url: Optional[str] = None
    
    @staticmethod
    def from_dict(data: dict) -> "OutfitCreateDTO":
        return OutfitCreateDTO(
            styleTag=data.get('styleTag'),
            occasionTag=data.get('occasionTag'),
            name=data.get('name'),
            weather=data.get('weather'),
            season=data.get('season'),
            img_url=data.get('img_url'),
        )

@dataclass
class OutfitItemViewDTO:
    id: int
    outfits_id: int
    category: str
    name: str

    @staticmethod
    def from_model(item: OutfitItem) -> "OutfitItemViewDTO":
        return OutfitItemViewDTO(
            id=item.id,
            outfits_id=item.outfits_id,
            category=item.category,
            name=item.name
        )