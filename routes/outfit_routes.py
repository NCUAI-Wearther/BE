from collections import defaultdict
import datetime
import math
import random
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sklearn.neighbors import NearestNeighbors
import numpy as np

from models import db, Favorite, Outfit, OutfitItem
from repositories import FavoriteRepository, OutfitItemRepository, OutfitRepository
from dto.outfit_dto import OutfitCreateDTO, OutfitItemViewDTO, OutfitViewDTO

outfit_bp = Blueprint('outfit_bp', __name__)

@outfit_bp.route('/', methods=['POST'])
def create_outfit():
    data = request.get_json()
    outfit_dto = OutfitCreateDTO.from_dict(data)

    outfit = Outfit(
        isRain=outfit_dto.isRain,
        weather_condition=outfit_dto.weather_condition,
        style_tag=outfit_dto.style_tag,
        occasion_tag=outfit_dto.occasion_tag,
        image_url=outfit_dto.image_url,
        created_at=datetime.datetime.now()
    )

    newOutfits = OutfitRepository.add(outfit)

    return jsonify({'message': 'Favorite add successfully!','outfits_id':newOutfits.id} ), 201

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

@outfit_bp.route('/<int:outfits_id>', methods=['GET'])
def get_outfits(outfits_id):
    outfits = OutfitRepository.get_by_id(outfits_id)
    
    if not outfits:
        return jsonify({'message': 'No outfit outfits found.', 'outfits': []}), 404

    return jsonify({
        'outfits': OutfitViewDTO.from_model(outfits)
    }), 200
    
@outfit_bp.route('/outfit_items/<int:outfits_id>', methods=['GET'])
def get_outfit_items(outfits_id):
    items = OutfitItemRepository.get_by_outfits_id(outfits_id)
    
    if not items:
        return jsonify({'message': 'No outfit items found.', 'items': []}), 404

    return jsonify({
        'items': [OutfitItemViewDTO.from_model(item) for item in items]
    }), 200

def map_temp_to_condition(temper:int):
    weather_condition = '舒適'
    if temper >= 35:
        weather_condition = '炎熱'
    elif temper >=28:
        weather_condition = '溫暖'
    elif temper >=23:
        weather_condition = '舒適'
    elif temper >=15:
        weather_condition = '涼爽'
    else:
        weather_condition = '寒冷'

    return weather_condition


def preference_filter(users_id, weather_matched_ids):
    prefs = UserPreference.query.filter_by(users_id=users_id).all()
    style_tags = {p.style_tag for p in prefs}
    occasion_tags = {p.occasion_tag for p in prefs}

    preference_matches = Outfit.query.filter(
        Outfit.id.in_(weather_matched_ids),
        Outfit.style_tag.in_(style_tags),
        Outfit.occasion_tag.in_(occasion_tags)
    ).all()
    return preference_matches

def get_user_tag_vectors():
    from collections import defaultdict
    all_tags = set()

    user_tags = defaultdict(set)
    records = db.session.query(Favorite.users_id, Outfit.style_tag, Outfit.occasion_tag)\
        .join(Outfit, Favorite.outfits_id == Outfit.id).all()

    for user_id, style_tag, occasion_tag in records:
        user_tags[user_id].add(style_tag)
        user_tags[user_id].add(occasion_tag)
        all_tags.update([style_tag, occasion_tag])

    all_tags = sorted(list(all_tags))
    tag_index = {tag: idx for idx, tag in enumerate(all_tags)}

    user_vectors = {}
    for user_id, tags in user_tags.items():
        vector = [0] * len(all_tags)
        for tag in tags:
            if tag in tag_index:
                vector[tag_index[tag]] = 1
        user_vectors[user_id] = vector

    return user_vectors, tag_index

def find_similar_users_knn(target_user_id, k=3):
    user_vectors, _ = get_user_tag_vectors()
    if target_user_id not in user_vectors:
        return []

    user_ids = list(user_vectors.keys())
    vectors = np.array([user_vectors[uid] for uid in user_ids])

    if len(user_ids) <= 1:
        return [] 

    n_neighbors = min(k + 1, len(user_ids))
    model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
    model.fit(vectors)

    target_idx = user_ids.index(target_user_id)
    distances, indices = model.kneighbors([user_vectors[target_user_id]])

    similar_users = [user_ids[i] for i in indices[0] if user_ids[i] != target_user_id]
    return similar_users

def similar_filter(users_id, weather_matched_ids):
    similar_user_ids = find_similar_users_knn(users_id, k=5)
    if not similar_user_ids:
        return []

    outfits = db.session.query(Favorite.outfits_id)\
        .filter(
            Favorite.users_id.in_(similar_user_ids),
            Favorite.outfits_id.in_(weather_matched_ids)
        ).distinct().all()

    return list(set(outfit_id for (outfit_id,) in outfits))


def popular_filter(weather_matched_ids):
    popular = db.session.query(
        Favorite.outfits_id,
        func.count(Favorite.users_id).label("count")
    ).filter(
        Favorite.outfits_id.in_(weather_matched_ids)
    ).group_by(
        Favorite.outfits_id
    ).order_by(
        func.count(Favorite.users_id).desc()
    ).limit(10).all()

    return popular

def latest_filter(weather_matched_ids):
    latest_outfits = Outfit.query.filter(Outfit.id.in_(weather_matched_ids))\
        .order_by(Outfit.created_at.desc()).limit(10).all()
    return latest_outfits
    
def calculate_popularity_score(fav_count, created_at, decay_lambda=0.01):
    days_passed = (datetime.datetime.now() - created_at).days
    decay = math.exp(-decay_lambda * days_passed)
    return fav_count * decay

@outfit_bp.route('/rcm/', methods=['POST'])
def get_rcm_outfit():
    data = request.get_json()
    users_id = data['users_id']
    isRain = data['isRain']
    temper = data['temper']
    
    weather_condition = map_temp_to_condition(temper)
    
    candidate_recommendations = []
    used_ids = set()
    
    weights = {
        'preference_style': 5,
        'similar_users': 4,
        'popular': 3,
        'latest': 2,
        'fallback_popular': 1,
        'fallback_latest': 1
    }

    # 1. 找出符合當前天氣的穿搭
    weather_matched_outfits = Outfit.query.filter_by(
        weather_condition=weather_condition,
        isRain=isRain
    ).all()
    weather_matched_ids = [o.id for o in weather_matched_outfits]

    # 2. 使用者偏好風格與場合
    preference_matches = preference_filter(users_id, weather_matched_ids)
    for outfit in preference_matches:
        if outfit.id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit.id,
                "tag": "preference_style",
                "score": weights['preference_style']
            })
            used_ids.add(outfit.id)
    
    # Step 3: 相似使用者收藏
    sim_user_fav_ids = similar_filter(users_id, weather_matched_ids)
    for outfit_id in sim_user_fav_ids:
        if outfit_id in weather_matched_ids and outfit_id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit_id,
                "tag": "similar_users",
                "score": weights['similar_users']
            })
            used_ids.add(outfit_id)

    # Step 4: 最多人收藏
    popular_raw = popular_filter(weather_matched_ids)
    outfit_created_map = {o.id: o.created_at for o in weather_matched_outfits}
    
    for outfit_id, fav_count in popular_raw:
        if outfit_id in weather_matched_ids and outfit_id not in used_ids:
            created_at = outfit_created_map.get(outfit_id, datetime.datetime.now())
            popularity_score = calculate_popularity_score(fav_count, created_at)
            weighted_score = popularity_score * weights['popular']
            candidate_recommendations.append({
                "outfits_id": outfit_id,
                "tag": "popular",
                "score": weighted_score
            })
            used_ids.add(outfit_id)
            
     # 5. 加入最多人收藏的熱門穿搭（符合天氣）
    latest_outfits = latest_filter(weather_matched_ids)
    for outfit in latest_outfits:
        if outfit.id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit.id,
                "tag": "latest",
                "score": weights['latest']
            })
            used_ids.add(outfit.id)
    
    # Step 6: 如果候選清單為空，選擇不分天氣的熱門穿搭作為 fallback
    if not candidate_recommendations:
        fallback_popular = db.session.query(
            Favorite.outfits_id, func.count(Favorite.users_id).label("count")
        ).group_by(Favorite.outfits_id).order_by(func.count(Favorite.users_id).desc()).limit(10).all()

        if fallback_popular:
            for o_id, fav_count in fallback_popular:
                created_at = Outfit.query.get(o_id).created_at
                popularity_score = calculate_popularity_score(fav_count, created_at)
                weighted_score = popularity_score * weights['fallback_popular']
                candidate_recommendations.append({
                    "outfits_id": o_id,
                    "tag": "fallback_popular",
                    "score": weighted_score
                })
        else:
            fallback_latest = Outfit.query.order_by(Outfit.created_at.desc()).limit(10).all()
            for outfit in fallback_latest:
                candidate_recommendations.append({
                    "outfits_id": outfit.id,
                    "tag": "fallback_latest",
                    "score": weights['fallback_latest']
                })

    candidate_recommendations.sort(key=lambda x: x['score'], reverse=True)
    final_recommendations = candidate_recommendations[:3]

    return jsonify(final_recommendations), 200