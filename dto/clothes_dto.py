from dataclasses import dataclass
from typing import Optional
from models import Cloth

@dataclass
class ClotheViewDTO:
    id: int
    brand: str
    category: str
    name: str
    color: str
    product_pic_url:str
    link_url: str
    price: int
    model_pic_url:Optional[str] = None

    @staticmethod
    def from_dict(cloth: Cloth) -> "ClotheViewDTO":
        return ClotheViewDTO(
            id=cloth.id,
            brand=cloth.brand,
            category=cloth.category,
            name=cloth.name,
            color=cloth.color,
            product_pic_url=cloth.product_pic_url,
            model_pic_url=cloth.model_pic_url,
            link_url=cloth.link_url,
            price=cloth.price
        )