import datetime
from flask import Blueprint, jsonify, request

from models import Outfit, OutfitItem
from repositories import OutfitItemRepository, OutfitRepository
from dto.outfit_dto import OutfitCreateDTO, OutfitItemViewDTO

outfit_bp = Blueprint('outfit_bp', __name__)

@outfit_bp.route('/', methods=['POST'])
def create_outfit():
    data = request.get_json()
    outfit_dto = OutfitCreateDTO.from_dict(data)

    outfit = Outfit(
        style_tag=outfit_dto.style_tag,
        occasion_tag=outfit_dto.occasion_tag,
        name=outfit_dto.name,
        weather=outfit_dto.weather,
        season=outfit_dto.season,
        created_at=datetime.datetime.now()
    )
    
    OutfitRepository.add(outfit)

    return jsonify({'message': 'Favorite add successfully!'}), 201

@outfit_bp.route('/outfit_items', methods=['POST'])
def create_outfit_items():
    data = request.get_json()
    labels = ['Top', 'Bottom','Outerwear','Hat','Socks','Shoes']
    id = data['outfits_id']

    if data['category'] not in labels:
        return jsonify({'message': 'Category not allowed!'}), 404

    if data['name'] == None:
            return jsonify({'message': 'name not found!'}), 404

    item = OutfitItem(
        outfits_id=id,
        category=data['category'],
        name=data['name'],
    )
    
    item = OutfitItemRepository.add(item)

    return jsonify({
        'message': 'Item added successfully!',
        'item': OutfitItemViewDTO.from_model(item)
    }), 201

@outfit_bp.route('/outfit_items/<int:outfits_id>', methods=['GET'])
def get_outfit_items(outfits_id):
    items = OutfitItemRepository.get_by_outfits_id(outfits_id)
    
    if not items:
        return jsonify({'message': 'No outfit items found.', 'items': []}), 404

    return jsonify({
        'items': [OutfitItemViewDTO.from_model(item) for item in items]
    }), 200
    
@outfit_bp.route('/rcm/<int:outfits_id>', methods=['GET'])
def get_rcm_outfit(users_id):
    return jsonify({
        'test': "test"
    }), 200