from flask import Blueprint, current_app, request, jsonify

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt

from repositories import TryOnRepository, UserRepository, FavoriteRepository, PostRepository
from models import User
from dto.user_dto import FavoriteViewDTO, PostViewDTO, TryonViewDTO, UserRegisterDTO, UserLoginDTO, UserUpdateDTO, UserViewDTO

user_bp = Blueprint('user_bp', __name__)

# region user
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = UserRepository.get_by_id(data['users_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


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
        profile_pic_url=user_dto.profile_pic_url,
        created_at = datetime.datetime.now()
    )
    
    UserRepository.add(new_user)

    return jsonify({'message': 'User created successfully!'}), 201


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_dto = UserLoginDTO.from_dict(data)
    user = UserRepository.get_by_email(data['email'])
    
    if not user or not check_password_hash(user.password_hash, user_dto.password):
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = jwt.encode({
        'users_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token}), 200


@user_bp.route('/<int:users_id>', methods=['GET'])
def get_user(users_id):
    user = UserRepository.get_by_id(users_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    return jsonify(UserViewDTO.from_model(user)), 200


@user_bp.route('/<int:users_id>', methods=['PUT'])
def update_user(users_id):
    data = request.get_json()
    user_dto = UserUpdateDTO.from_dict(data)
    user = UserRepository.get_by_id(users_id)

    if not user:
        return jsonify({'message': 'User not found!'}), 404

    if user_dto.username != None:
        user.username = user_dto.username
    
    if user_dto.email != None:
        user.email = user_dto.email
    
    if user_dto.password != None:
        user.password_hash = generate_password_hash(user_dto.password)

    if user_dto.gender != None:
        user.gender = user_dto.gender

    if user_dto.birthday != None:
        user.birthday = user_dto.birthday

    if user_dto.profile_pic_url != None:
        user.profile_pic_url = user_dto.profile_pic_url

    UserRepository.update(user)

    return jsonify({'message': 'User updated successfully!'}), 200

@user_bp.route('/upload_photo/<int:users_id>', methods=['POST'])
def upload_photo(users_id):
    data = request.get_json()
    imgFile = data['imgFile']

    if not imgFile:
        return jsonify({'message': 'imgFile cannot be null!'}), 404

    user = UserRepository.get_by_id(users_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    # user.photo_pic_url = #todo
    url=imgFile
    user.photo_pic_url= url

    UserRepository.update(user)
    return jsonify({'message': 'User photo upload successfully!', 'photo_pic_url': url}), 200
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


# region tryon
@user_bp.route('/tryons/<int:users_id>', methods=['GET'])
def get_tryons(users_id):
    tryOns = TryOnRepository.get_by_users_id(users_id)
    if not tryOns:
        return jsonify({'message': 'Tryon not found!', 'tryOns': []}), 404
    
    response = []
    for tryOn in tryOns:
        response.append(TryonViewDTO.from_model(tryOn))
    
    return jsonify({'tryOns':response}), 200
# endregion