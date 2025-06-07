import json
import os
from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from models import db, Favorite, OutfitItem, Outfit
from dto.clothes_dto import ClotheViewDTO

from ckip_transformers.nlp import CkipWordSegmenter

clothes_bp = Blueprint('clothes_bp', __name__)

ws_driver = CkipWordSegmenter(model="bert-base")


@clothes_bp.route('/<int:users_id>', methods=['GET'])
def get_all_clothes(users_id):
    category_filter = request.args.get('category', None)

    json_path = './uniqlo_products.json'
    if not os.path.exists(json_path):
        return jsonify({'message': 'Clothes file not found!', 'clothes': []}), 404
    with open(json_path, 'r', encoding='utf-8') as f:
        clothes = json.load(f)

    if category_filter:
        clothes = [c for c in clothes if c.get('category') == category_filter]

    if not clothes:
        return jsonify({'message': 'No clothes found for this category!', 'clothes': []}), 404

    favorites = db.session.query(Favorite).filter(Favorite.users_id == users_id).all()
    outfit_ids = [f.outfits_id for f in favorites]

    if not outfit_ids:
        return jsonify({'clothes': [ClotheViewDTO.from_dict(c) for c in clothes]}), 200

    outfit_items = (
        db.session.query(OutfitItem)
        .filter(
            and_(
                OutfitItem.outfits_id.in_(outfit_ids),
                OutfitItem.category == category_filter
            )
        ).all()
    )

    if not outfit_items:
        return jsonify({'clothes': [ClotheViewDTO.from_dict(c) for c in clothes]}), 200

    item_names = [item.name for item in outfit_items]
    item_tokens_list = ws_driver(item_names)
    item_token_sets = [set(tokens) for tokens in item_tokens_list]

    def get_score(cloth):
        cloth_tokens = set(ws_driver([cloth['name']])[0])
        max_overlap = max(
            (len(cloth_tokens & item_tokens) for item_tokens in item_token_sets),
            default=0
        )
        return max_overlap

    clothes.sort(key=lambda c: get_score(c), reverse=True)

    return jsonify({'clothes': [ClotheViewDTO.from_dict(c) for c in clothes]}), 200
