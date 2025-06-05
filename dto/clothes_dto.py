from dataclasses import dataclass
from typing import Optional
from models import Cloth

@dataclass
class ClotheViewDTO:
    id: int
    brand: str
    category: str
    name: str
    product_pic_url:str
    link_url: str
    price: int

    @staticmethod
    def from_dict(cloth: Cloth) -> "ClotheViewDTO":
        return ClotheViewDTO(
            id=cloth.id,
            brand=cloth.brand,
            category=cloth.category,
            name=cloth.name,
            product_pic_url=cloth.product_pic_url,
            link_url=cloth.link_url,
            price=cloth.price
        )