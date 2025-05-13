from flask import Blueprint, jsonify, request
from models import TryOn
from repositories import TryOnRepository
from dto.tryon_dto import TryOnDTO

tryon_bp = Blueprint('tryon_bp', __name__)

@tryon_bp.route('/', methods=['POST'])
def add_tryon():
    data = request.get_json()
    tryon_dto = TryOnDTO.from_dict(data)

    # if FavoriteRepository.get_by_user_and_outfits_id(favorite_dto.users_id):

    tryOn = TryOn(
        users_id=tryon_dto.users_id,
        clothes_id=tryon_dto.clothes_id,
        category=tryon_dto.category,
    )
    
    TryOnRepository.add(tryOn)

    return jsonify({'message': 'tryOn add successfully!'}), 201


@tryon_bp.route('/', methods=['DELETE'])
def delete_tryon():
    clothes_id = request.args.get('clothes_id')
    user_id = request.args.get('user_id')

    tryOn = TryOnRepository.get_by_id(clothes_id, user_id)

    if not tryOn:
        return jsonify({'message': 'tryOn not found!'}), 404
    
    TryOnRepository.delete(tryOn)
    
    return jsonify({'message': 'tryOn deleted successfully!'}), 200