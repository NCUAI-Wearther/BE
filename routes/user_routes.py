from flask import Blueprint, current_app, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from repositories import UserRepository, FavoriteRepository, LikeRepository
from schemas import UserSchema, FavoriteSchema, LikeSchema
import jwt
import datetime
from functools import wraps

user_bp = Blueprint('user_bp', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
favorite_schema = FavoriteSchema()
favorites_schema = FavoriteSchema(many=True)
like_schema = LikeSchema()
likes_schema = LikeSchema(many=True)

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
            current_user = UserRepository.get_by_id(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if UserRepository.get_by_username(data['username']):
        return jsonify({'message': 'Username already exists!'}), 409
    
    if UserRepository.get_by_email(data['email']):
        return jsonify({'message': 'Email already exists!'}), 409

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        profile_pic_url=data.get('profile_pic_url')
    )
    
    UserRepository.add(new_user)
    
    return jsonify({'message': 'User created successfully!'}), 201


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = UserRepository.get_by_email(data['email'])
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token}), 200


@user_bp.route('/', methods=['GET'])
def get_all_users():
    users = UserRepository.get_all()
    return jsonify(users_schema.dump(users)), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UserRepository.get_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    return jsonify(user_schema.dump(user)), 200


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = UserRepository.get_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    data = request.get_json()
 
    if 'username' in data:
        existing_user = UserRepository.get_by_username(data['username'])
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Username already exists!'}), 409
        user.username = data['username']
    
    if 'email' in data:
        existing_user = UserRepository.get_by_email(data['email'])
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Email already exists!'}), 409
        user.email = data['email']
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    
    if 'profile_pic_url' in data:
        user.profile_pic_url = data['profile_pic_url']
    
    UserRepository.update()
    
    return jsonify({'message': 'User updated successfully!'}), 200


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = UserRepository.get_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    UserRepository.delete(user)
    
    return jsonify({'message': 'User deleted successfully!'}), 200


@user_bp.route('/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(current_user, user_id):

    favorites = FavoriteRepository.get_by_user(user_id)
    
    return jsonify(favorites_schema.dump(favorites)), 200


@user_bp.route('/<int:user_id>/likes', methods=['GET'])
def get_user_likes(current_user, user_id):

    likes = LikeRepository.get_by_user(user_id)
    
    return jsonify(likes_schema.dump(likes)), 200