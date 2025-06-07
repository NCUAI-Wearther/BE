from dataclasses import dataclass
from typing import Optional

class ClotheViewDTO:
    @staticmethod
    def from_dict(data):
        return {
            'brand': data.get('brand'),
            'gender': data.get('gender'),
            'category': data.get('category'),
            'name': data.get('name'),
            'preview_pic_url': data.get('preview_pic_url'),
            'link_url': data.get('link_url'),
            'price': data.get('price'),
            'product_pic_url': data.get('product_pic_url')
        }
