import datetime
from flask import Blueprint, jsonify, request

from models import Favorite
from repositories import FavoriteRepository
from dto.favorite_dto import FavoriteAddDTO

favorite_bp = Blueprint('favorite_bp', __name__)

@favorite_bp.route('/', methods=['POST'])
def add_favorite():
    data = request.get_json()
    favorite_dto = FavoriteAddDTO.from_dict(data)

    favorite = Favorite(
        users_id=favorite_dto.users_id,
        outfits_id=favorite_dto.outfits_id,
        created_at=datetime.datetime.now()
    )

    FavoriteRepository.add(favorite)

    return jsonify({'message': 'Favorite add successfully!'}), 201

@favorite_bp.route('/', methods=['DELETE'])
def delete_favorite():
    data = request.get_json()
    
    if not data['users_id'] or not data['outfits_id']:
        return jsonify({'message': 'Favorite not found!'}), 404
    
    status = FavoriteRepository.remove_favorite(data['users_id'], data['outfits_id'])
    if status == True:
        return jsonify({'message': 'Favorite deleted successfully!'}), 200
    else:
        return jsonify({'message': 'Favorite deleted failed!'}), 404