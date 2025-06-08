from collections import defaultdict
import datetime
import json
import math
import random
from flask import Blueprint, jsonify, request
import requests
from sqlalchemy import func
from sklearn.neighbors import NearestNeighbors
import numpy as np

from models import db, Favorite, Outfit, OutfitItem
from repositories import FavoriteRepository, OutfitItemRepository, OutfitRepository
from dto.outfit_dto import OutfitCreateDTO, OutfitItemViewDTO, OutfitViewDTO

outfit_bp = Blueprint('outfit_bp', __name__)

# region basic
@outfit_bp.route('/', methods=['POST'])
def create_outfit():
    data = request.get_json()
    if not data or "clothes" not in data:
        return jsonify({"error": "缺少clothes欄位"}), 400
    
    clothes_list = data["clothes"]
    outfit = Outfit()
    
    annotate_outfit(clothes_list, outfit)
    outfit.created_at=datetime.datetime.now()
    outfit.image_url=data['image_url']
    
    # outfit = Outfit(
    #     isRain=outfit_dto.isRain,
    #     weather_condition=outfit_dto.weather_condition,
    #     style_tag=outfit_dto.style_tag,
    #     occasion_tag=outfit_dto.occasion_tag,
    #     image_url=outfit_dto.image_url,
    #     created_at=datetime.datetime.now()
    # )

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
# endRegion

# region Gemini

GEMINI_API_KEY = "AIzaSyCfu-lNQxlHIjxUGz4nHiVPvwgePjB8mdg"
def call_gemini_api(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def build_prompt(clothes_list):
    clothes_str = "，".join(clothes_list)
    prompt = f"""
請根據以下穿搭描述，分析此穿搭適合的天氣與風格，並以標準化格式輸出。

條件限制：
- 「是否下雨」只能輸出 0(否) 或 1(是)
- 「溫度感受」只能選擇：[寒冷, 涼爽, 舒適, 溫暖, 炎熱]
- 「風格」只能選擇以下一種：[知性文青, 中性, 優雅, 甜美, Y2K, 簡約, 復古, 歐美, 韓系, 英倫, 休閒]
- 「場合」只能選擇以下一種：[日常, 約會, 正式, 聚會, 戶外活動]
- 「服裝說明」請簡潔用中文完整句子說明整體穿搭，不要超過25字

穿搭描述：
[{clothes_str}]

請依下列順序與格式輸出，不需要加標籤或 JSON 結構：
["是否下雨(0 或 1)", "溫度感受", "風格", "場合", "服裝描述"]
"""
    return prompt

def parse_gemini_response(api_response):
    try:
        text = api_response['candidates'][0]['content']['parts'][0]['text'].strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        data = json.loads(text)
        return data
    except Exception as e:
        print("解析回傳失敗:", e)
        return None
    
def annotate_outfit(clothes_list, outfits:OutfitCreateDTO):
    if not isinstance(clothes_list, list) or not all(isinstance(i, str) for i in clothes_list):
        return jsonify({"error": "clothes必須是字串陣列"}), 400

    prompt = build_prompt(clothes_list)
    api_response = call_gemini_api(GEMINI_API_KEY, prompt)
    if not api_response:
        return jsonify({"error": "呼叫AI服務失敗"}), 500
    
    labels = parse_gemini_response(api_response)
    if not labels:
        return jsonify({"error": "解析AI回應失敗"}), 500

    outfits.isRain=False if labels[0] == "0" else True
    outfits.weather_condition=labels[1]
    outfits.style_tag=labels[2]
    outfits.occasion_tag=labels[3]
    outfits.description=labels[4]
    
    return outfits

#endRegion


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
    # 從使用者收藏的穿搭中，查詢其風格和場合標籤
    user_favorited_outfits_tags = db.session.query(Outfit.style_tag, Outfit.occasion_tag) \
        .join(Favorite, Favorite.outfits_id == Outfit.id) \
        .filter(Favorite.users_id == users_id) \
        .distinct() \
        .all()

    style_tags = {tag for tag, _ in user_favorited_outfits_tags if tag is not None}
    occasion_tags = {tag for _, tag in user_favorited_outfits_tags if tag is not None}

    if not style_tags and not occasion_tags:
        return []

    preference_matches = Outfit.query.filter(
        Outfit.id.in_(weather_matched_ids),
        Outfit.style_tag.in_(style_tags),
        Outfit.occasion_tag.in_(occasion_tags)
    ).all()
    return preference_matches

# --- 協同過濾 - 標籤相似度 ---
def get_user_tag_vectors():
    all_tags = set()
    user_tags = defaultdict(set)
    records = db.session.query(Favorite.users_id, Outfit.style_tag, Outfit.occasion_tag)\
        .join(Outfit, Favorite.outfits_id == Outfit.id).all()

    for user_id, style_tag, occasion_tag in records:
        if style_tag:
            user_tags[user_id].add(style_tag)
            all_tags.add(style_tag)
        if occasion_tag:
            user_tags[user_id].add(occasion_tag)
            all_tags.add(occasion_tag)

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

def find_similar_users_by_tags(target_user_id, k=3):
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
    distances, indices = model.kneighbors([user_vectors[target_idx]])

    similar_users = [user_ids[i] for i in indices[0] if user_ids[i] != target_user_id]
    return similar_users

# --- 協同過濾 - 共同收藏項目相似度 (新增部分) ---
def get_user_item_vectors():
    all_outfits_ids = set()
    user_favorited_items = defaultdict(set) # user_id -> set of favorited outfit_ids

    records = db.session.query(Favorite.users_id, Favorite.outfits_id).all()

    for user_id, outfit_id in records:
        user_favorited_items[user_id].add(outfit_id)
        all_outfits_ids.add(outfit_id)

    all_outfits_ids_sorted = sorted(list(all_outfits_ids))
    outfit_id_index = {outfit_id: idx for idx, outfit_id in enumerate(all_outfits_ids_sorted)}

    user_vectors = {}
    for user_id, favorited_ids in user_favorited_items.items():
        vector = [0] * len(all_outfits_ids_sorted)
        for outfit_id in favorited_ids:
            if outfit_id in outfit_id_index:
                vector[outfit_id_index[outfit_id]] = 1
        user_vectors[user_id] = vector
    return user_vectors, outfit_id_index

def find_similar_users_by_outfits(target_user_id, k=3):
    user_vectors, _ = get_user_item_vectors()
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
    distances, indices = model.kneighbors([user_vectors[target_idx]])

    similar_users = [user_ids[i] for i in indices[0] if user_ids[i] != target_user_id]
    return similar_users
# --- 共同過濾函數 (通用於兩種類型的相似用戶) ---
def filter_by_similar_users_favs(similar_user_ids, weather_matched_ids):
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


# recommend
@outfit_bp.route('/rcm/', methods=['POST'])
def get_rcm_outfit():
    data = request.get_json()
    users_id = data.get('users_id')
    isRain = data.get('isRain')
    temper = data.get('temper')
    
    if users_id is None or isRain is None or temper is None:
        return jsonify({"error": "請提供 users_id, isRain, 和 temper 參數。"}), 400

    weather_condition = map_temp_to_condition(temper)
    candidate_recommendations = []
    used_ids = set()

    weights = {
        'preference_style': 5,
        'similar_users_tags': 4,
        'similar_users_outfits': 4,
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
    
    outfit_id_to_model_map = {o.id: o for o in weather_matched_outfits}

    # 2. 使用者偏好風格與場合 (從收藏中提取)
    preference_matches = preference_filter(users_id, weather_matched_ids)
    for outfit in preference_matches:
        if outfit.id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit.id,
                "tag": "preference_style",
                "score": weights['preference_style']
            })
            used_ids.add(outfit.id)
    
    # 3. 相似使用者收藏 (基於標籤相似性)
    sim_users_by_tags_ids = find_similar_users_by_tags(users_id, k=5)
    sim_user_fav_ids_tags = filter_by_similar_users_favs(sim_users_by_tags_ids, weather_matched_ids)
    for outfit_id in sim_user_fav_ids_tags:
        if outfit_id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit_id,
                "tag": "similar_users_tags",
                "score": weights['similar_users_tags']
            })
            used_ids.add(outfit_id)

    # 4. 相似使用者收藏 (基於共同收藏項目相似性 - 新增)
    sim_users_by_outfits_ids = find_similar_users_by_outfits(users_id, k=5)
    sim_user_fav_ids_outfits = filter_by_similar_users_favs(sim_users_by_outfits_ids, weather_matched_ids)
    for outfit_id in sim_user_fav_ids_outfits:
        if outfit_id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit_id,
                "tag": "similar_users_outfits",
                "score": weights['similar_users_outfits']
            })
            used_ids.add(outfit_id)

    # 5. 最多人收藏 (符合天氣)
    popular_raw = popular_filter(weather_matched_ids)
    for outfit_id, fav_count in popular_raw:
        if outfit_id not in used_ids:
            outfit_model = outfit_id_to_model_map.get(outfit_id)
            if outfit_model:
                created_at = outfit_model.created_at
                popularity_score = calculate_popularity_score(fav_count, created_at)
                weighted_score = popularity_score * weights['popular']
                candidate_recommendations.append({
                    "outfits_id": outfit_id,
                    "tag": "popular",
                    "score": weighted_score
                })
                used_ids.add(outfit_id)
            
    # 6. 最新建立的穿搭 (符合天氣)
    latest_outfits = latest_filter(weather_matched_ids)
    for outfit in latest_outfits:
        if outfit.id not in used_ids:
            candidate_recommendations.append({
                "outfits_id": outfit.id,
                "tag": "latest",
                "score": weights['latest']
            })
            used_ids.add(outfit.id)
    
    # 7. Fallback 機制
    if not candidate_recommendations:
        print("沒有找到符合當前天氣的穿搭，將推薦最多人收藏或最新穿搭作為 fallback。")
        fallback_popular = db.session.query(
            Favorite.outfits_id, func.count(Favorite.users_id).label("count")
        ).group_by(Favorite.outfits_id).order_by(func.count(Favorite.users_id).desc()).limit(10).all()

        if fallback_popular:
            for o_id, fav_count in fallback_popular:
                fallback_outfit_model = OutfitRepository.get_by_id(o_id)
                if fallback_outfit_model:
                    created_at = fallback_outfit_model.created_at
                    popularity_score = calculate_popularity_score(fav_count, created_at)
                    weighted_score = popularity_score * weights['fallback_popular']
                    candidate_recommendations.append({
                        "outfits_id": o_id,
                        "tag": "fallback_popular",
                        "score": weighted_score
                    })
        
        if not candidate_recommendations:
            fallback_latest = Outfit.query.order_by(Outfit.created_at.desc()).limit(10).all()
            for outfit in fallback_latest:
                candidate_recommendations.append({
                    "outfits_id": outfit.id,
                    "tag": "fallback_latest",
                    "score": weights['fallback_latest']
                })

    candidate_recommendations.sort(key=lambda x: x['score'], reverse=True)
    final_recommendations = candidate_recommendations[:3]

    if not final_recommendations:
        return jsonify([]), 200

    recommended_outfit_ids = [rec['outfits_id'] for rec in final_recommendations]
    recommended_outfits_models = Outfit.query.filter(Outfit.id.in_(recommended_outfit_ids)).all()
    
    ordered_recommendations = []
    for r_id in recommended_outfit_ids:
        for outfit_model in recommended_outfits_models:
            if outfit_model.id == r_id:
                ordered_recommendations.append(OutfitViewDTO.from_model(outfit_model))
                break

    return jsonify(ordered_recommendations), 200