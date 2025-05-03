from flask import Blueprint, request, jsonify
from models import ClothingItem
from repositories import ClothingItemRepository
from schemas import ClothingItemSchema
from routes.user_routes import token_required

clothing_bp = Blueprint('clothing_bp', __name__)
clothing_item_schema = ClothingItemSchema()
clothing_items_schema = ClothingItemSchema(many=True)


@clothing_bp.route('/', methods=['GET'])
def get_all_clothing_items():
    clothing_items = ClothingItemRepository.get_all()
    return jsonify(clothing_items_schema.dump(clothing_items)), 200


@clothing_bp.route('/<int:item_id>', methods=['GET'])
def get_clothing_item(item_id):
    clothing_item = ClothingItemRepository.get_by_id(item_id)
    
    if not clothing_item:
        return jsonify({'message': 'Clothing item not found!'}), 404
    
    return jsonify(clothing_item_schema.dump(clothing_item)), 200


@clothing_bp.route('/', methods=['POST'])
def create_clothing_item(current_user):
    data = request.get_json()
    
    # Create new clothing item
    new_clothing_item = ClothingItem(
        name=data['name'],
        image_url=data['image_url'],
        category=data['category'],
        temperature=data.get('temperature', 0),
        material=data.get('material'),
        color=data.get('color')
    )
    
    ClothingItemRepository.add(new_clothing_item)
    
    return jsonify(clothing_item_schema.dump(new_clothing_item)), 201


@clothing_bp.route('/<int:item_id>', methods=['PUT'])
def update_clothing_item(current_user, item_id):
    clothing_item = ClothingItemRepository.get_by_id(item_id)
    
    if not clothing_item:
        return jsonify({'message': 'Clothing item not found!'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        clothing_item.name = data['name']
    
    if 'image_url' in data:
        clothing_item.image_url = data['image_url']
    
    if 'category' in data:
        clothing_item.category = data['category']
    
    if 'temperature' in data:
        clothing_item.temperature = data['temperature']
    
    if 'material' in data:
        clothing_item.material = data['material']
    
    if 'color' in data:
        clothing_item.color = data['color']
    
    ClothingItemRepository.update()
    
    return jsonify(clothing_item_schema.dump(clothing_item)), 200


@clothing_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_clothing_item(current_user, item_id):
    clothing_item = ClothingItemRepository.get_by_id(item_id)
    
    if not clothing_item:
        return jsonify({'message': 'Clothing item not found!'}), 404
    
    ClothingItemRepository.delete(clothing_item)
    
    return jsonify({'message': 'Clothing item deleted successfully!'}), 200


@clothing_bp.route('/category/<string:category>', methods=['GET'])
def get_clothing_by_category(category):
    clothing_items = ClothingItemRepository.get_by_category(category)
    
    return jsonify(clothing_items_schema.dump(clothing_items)), 200


@clothing_bp.route('/temperature/<int:temp>', methods=['GET'])
def get_clothing_by_temperature(temp):
    clothing_items = ClothingItemRepository.get_by_temperature(temp)
    
    return jsonify(clothing_items_schema.dump(clothing_items)), 200