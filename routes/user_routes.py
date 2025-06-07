from collections import Counter
from flask import Blueprint, current_app, request, jsonify

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from repositories import  LikeRepository, OutfitRepository, UserRepository, FavoriteRepository, PostRepository
from models import db, User
from dto.user_dto import FavoriteViewDTO, LikeViewDTO, PostViewDTO, UserRegisterDTO, UserLoginDTO

user_bp = Blueprint('user_bp', __name__)

# region user

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_dto = UserRegisterDTO.from_dict(data)

    if UserRepository.get_by_email(user_dto.email):
        return jsonify({'message': 'Email already exists!'}), 409

    hashed_password = generate_password_hash(user_dto.password)
    
    new_user = User(
        username=user_dto.username,
        email=user_dto.email,
        password_hash=hashed_password,
        gender=user_dto.gender,
        birthday=user_dto.birthday,
        created_at = datetime.datetime.now()
    )
    
    UserRepository.add(new_user)

    return jsonify({'message': 'User created successfully!'}), 201
# endregion


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_dto = UserLoginDTO.from_dict(data)
    user = UserRepository.get_by_email(data['email'])
    
    if not user or not check_password_hash(user.password_hash, user_dto.password):
        return jsonify({'message': 'Wrong email or password'}), 401

    token = jwt.encode({
        'users_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'users_id': user.id}), 200

# endregion


# region favorite
@user_bp.route('/favorites/<int:users_id>', methods=['GET'])
def get_favorites(users_id):
    favorites = FavoriteRepository.get_by_users_id(users_id)
    if not favorites:
        return jsonify({'message': 'favorite not found!', 'favorites': []}), 404

    response = []
    for favorite in favorites:
        response.append(FavoriteViewDTO.from_model(favorite))

    return jsonify({'favorite':response}), 200

# endregion


# region like
@user_bp.route('/likes/<int:users_id>', methods=['GET'])
def get_likes(users_id):
    likes = LikeRepository.get_by_users_id(users_id)
    if not likes:
        return jsonify({'message': 'like not found!', 'likes': []}), 404

    response = []
    for like in likes:
        response.append(LikeViewDTO.from_model(like))

    return jsonify({'favorite':response}), 200

# endregion

# region post
@user_bp.route('/posts/<int:users_id>', methods=['GET'])
def get_posts(users_id):
    posts = PostRepository.get_by_users_id(users_id)
    if not posts:
        return jsonify({'message': 'post not found!', 'posts': []}), 404
    
    response = []
    for post in posts:
        response.append(PostViewDTO.from_model(post))
    
    return jsonify({'posts':response}), 200
# endregion
