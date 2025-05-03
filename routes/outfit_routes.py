from flask import Blueprint, request, jsonify
from models import Outfit, OutfitItem, StyleTag, OccasionTag
from repositories import OutfitRepository, StyleTagRepository, OccasionTagRepository, OutfitItemRepository, ClothingItemRepository, FavoriteRepository
from schemas import OutfitSchema, StyleTagSchema, OccasionTagSchema, OutfitItemSchema
from routes.user_routes import token_required

outfit_bp = Blueprint('outfit_bp', __name__)
outfit_schema = OutfitSchema()
outfits_schema = OutfitSchema(many=True)
style_schema = StyleTagSchema()
styles_schema = StyleTagSchema(many=True)
occasion_schema = OccasionTagSchema()
occasions_schema = OccasionTagSchema(many=True)
outfit_item_schema = OutfitItemSchema()
outfit_items_schema = OutfitItemSchema(many=True)

# region outfits
@outfit_bp.route('/', methods=['GET'])
def get_all_outfits():
    outfits = OutfitRepository.get_all()
    return jsonify(outfits_schema.dump(outfits)), 200


@outfit_bp.route('/<int:outfit_id>', methods=['GET'])
def get_outfit(outfit_id):
    outfit = OutfitRepository.get_by_id(outfit_id)
    
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404
    
    return jsonify(outfit_schema.dump(outfit)), 200


@outfit_bp.route('/', methods=['POST'])
def create_outfit():
    data = request.get_json()
    
    if 'styleTag_id' in data:
        style = StyleTagRepository.get_by_id(data['styleTag_id'])
    else:
        style = StyleTag(name=data.get('style_name', '無'))
        StyleTagRepository.add(style)
    
    if 'occasionTag_id' in data:
        occasion = OccasionTagRepository.get_by_id(data['occasionTag_id'])
        if not occasion:
            return jsonify({'message': 'OccasionTag not found!'}), 404
    else:
        occasion = OccasionTag(name=data.get('occasion_name', '無'))
        OccasionTagRepository.add(occasion)

    new_outfit = Outfit(
        styleTag_id=style.id,
        occasionTag_id=occasion.id,
        name=data['name'],
        weather_type=data['weather_type']
    )
    
    OutfitRepository.add(new_outfit)

    # 處理 outfit 的 items
    if 'items' in data:
        for item_data in data['items']:
            clothing_item = ClothingItemRepository.get_by_id(item_data['clothingItem_id'])
            if not clothing_item:
                return jsonify({'message': f'Clothing item with ID {item_data["clothingItem_id"]} not found!'}), 404
            
            outfit_item = OutfitItem(
                clothingItem_id=item_data['clothingItem_id'],
                outfits_id=new_outfit.id,
                category=item_data['category']
            )
            
            OutfitItemRepository.add(outfit_item)

    return jsonify(outfit_schema.dump(new_outfit)), 201

@outfit_bp.route('/<int:outfit_id>', methods=['PUT'])
def update_outfit(outfit_id):
    outfit = OutfitRepository.get_by_id(outfit_id)
    
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404
    
    data = request.get_json()

    if 'styleTag_id' in data:
        style = StyleTagRepository.get_by_id(data['styleTag_id'])
        if not style:
            return jsonify({'message': 'Style tag not found!'}), 404
        outfit.styleTag_id = data['styleTag_id']
    
    if 'occasionTag_id' in data:
        occasion = OccasionTagRepository.get_by_id(data['occasionTag_id'])
        if not occasion:
            return jsonify({'message': 'Occasion tag not found!'}), 404
        outfit.occasionTag_id = data['occasionTag_id']
    
    if 'name' in data:
        outfit.name = data['name']
    
    if 'weather_type' in data:
        outfit.weather_type = data['weather_type']
    
    OutfitRepository.update()
    
    return jsonify(outfit_schema.dump(outfit)), 200


@outfit_bp.route('/<int:outfit_id>', methods=['DELETE'])
def delete_outfit(outfit_id):
    outfit = OutfitRepository.get_by_id(outfit_id)
    
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404

    outfit_items = OutfitItemRepository.get_by_outfit(outfit_id)
    for item in outfit_items:
        OutfitItemRepository.delete(item)
    
    OutfitRepository.delete(outfit)
    
    return jsonify({'message': 'Outfit deleted successfully!'}), 200

# endregion

# region outfits items
@outfit_bp.route('/<int:outfit_id>/items', methods=['GET'])
def get_outfit_items(outfit_id):
    outfit = OutfitRepository.get_by_id(outfit_id)
    
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404
    
    outfit_items = OutfitItemRepository.get_by_outfit(outfit_id)
    
    return jsonify(outfit_items_schema.dump(outfit_items)), 200


@outfit_bp.route('/<int:outfit_id>/items', methods=['POST'])
def add_outfit_item(outfit_id):
    outfit = OutfitRepository.get_by_id(outfit_id)
    
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404
    
    data = request.get_json()

    clothing_item = ClothingItemRepository.get_by_id(data['clothingItem_id'])
    if not clothing_item:
        return jsonify({'message': 'Clothing item not found!'}), 404

    outfit_item = OutfitItem(
        clothingItem_id=data['clothingItem_id'],
        outfits_id=outfit_id,
        category=data['category']
    )
    
    OutfitItemRepository.add(outfit_item)
    
    return jsonify(outfit_item_schema.dump(outfit_item)), 201

@outfit_bp.route('/<int:outfit_id>/items/<int:item_id>', methods=['DELETE'])
def remove_outfit_item(outfit_id, item_id):
    outfit_item = OutfitItemRepository.get_by_id(item_id)
    
    if not outfit_item or outfit_item.outfits_id != outfit_id:
        return jsonify({'message': 'Outfit item not found!'}), 404
    
    OutfitItemRepository.delete(outfit_item)
    
    return jsonify({'message': 'Outfit item removed successfully!'}), 200

# endregion

# region tags
@outfit_bp.route('/weather/<string:weather_type>', methods=['GET'])
def get_outfits_by_weather(weather_type):
    outfits = OutfitRepository.get_by_weather(weather_type)
    
    return jsonify(outfits_schema.dump(outfits)), 200


@outfit_bp.route('/style/<int:style_id>', methods=['GET'])
def get_outfits_by_style(style_id):
    style = StyleTagRepository.get_by_id(style_id)
    if not style:
        return jsonify({'message': 'Style tag not found!'}), 404
    
    outfits = OutfitRepository.get_by_style(style_id)
    
    return jsonify(outfits_schema.dump(outfits)), 200


@outfit_bp.route('/occasion/<int:occasion_id>', methods=['GET'])
def get_outfits_by_occasion(occasion_id):
    occasion = OccasionTagRepository.get_by_id(occasion_id)
    if not occasion:
        return jsonify({'message': 'Occasion tag not found!'}), 404
    
    outfits = OutfitRepository.get_by_occasion(occasion_id)
    
    return jsonify(outfits_schema.dump(outfits)), 200


@outfit_bp.route('/styles', methods=['GET'])
def get_all_styles():
    styles = StyleTagRepository.get_all()
    
    return jsonify(styles_schema.dump(styles)), 200

@outfit_bp.route('/styles', methods=['POST'])
def create_style():
    data = request.get_json()

    existing_style = StyleTagRepository.get_by_name(data['name'])
    if existing_style:
        return jsonify({'message': 'Style tag already exists!'}), 409

    new_style = StyleTag(name=data['name'])
    
    StyleTagRepository.add(new_style)
    
    return jsonify(style_schema.dump(new_style)), 201

@outfit_bp.route('/occasions', methods=['GET'])
def get_all_occasions():
    occasions = OccasionTagRepository.get_all()
    
    return jsonify(occasions_schema.dump(occasions)), 200

@outfit_bp.route('/occasions', methods=['POST'])
def create_occasion(r):
    data = request.get_json()

    existing_occasion = OccasionTagRepository.get_by_name(data['name'])
    if existing_occasion:
        return jsonify({'message': 'Occasion tag already exists!'}), 409

    new_occasion = OccasionTag(name=data['name'])
    
    OccasionTagRepository.add(new_occasion)
    
    return jsonify(occasion_schema.dump(new_occasion)), 201

# endregion