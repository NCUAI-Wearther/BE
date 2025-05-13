import datetime
from flask import Blueprint, jsonify, request

from models import Cloth
from repositories import ClothRepository
from dto.clothes_dto import ClotheViewDTO

clothes_bp = Blueprint('clothes_bp', __name__)

@clothes_bp.route('/', methods=['GET'])
def getAll_clothes():
    clothes = ClothRepository.getAll()
    
    if not clothes:
        return jsonify({'message': 'clothes not found!', 'favorites': []}), 404

    response = []
    for cloth in clothes:
        response.append(ClotheViewDTO.from_dict(cloth))
        
    return jsonify({'clothes':response}), 200