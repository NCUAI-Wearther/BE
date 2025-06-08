from dataclasses import dataclass
import datetime
from typing import Optional
from models import Outfit, OutfitItem

@dataclass
class OutfitCreateDTO:
    isRain: str
    weather_condition:str
    style_tag: str
    occasion_tag: str
    image_url: Optional[str] = None
    description: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "OutfitCreateDTO":
        return OutfitCreateDTO(
            isRain=data.get('isRain'),
            weather_condition=data.get('weather_condition'),
            style_tag=data.get('style_tag'),
            occasion_tag=data.get('occasion_tag'),
            image_url=data.get('image_url'),
            description=data.get('description'),
        )

@dataclass
class OutfitViewDTO:
    id: int
    isRain: str
    weather_condition:str
    style_tag: str
    occasion_tag: str
    image_url: Optional[str] = None
    description: Optional[str] = None

    @staticmethod
    def from_model(outfit: Outfit) -> "OutfitViewDTO":
        return OutfitViewDTO(
            id=outfit.id,
            isRain=outfit.isRain,
            weather_condition=outfit.weather_condition,
            style_tag=outfit.style_tag,
            occasion_tag=outfit.occasion_tag,
            image_url=outfit.image_url,
            description = outfit.description,
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