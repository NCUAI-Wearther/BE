import datetime
from flask import Blueprint, jsonify, request

from models import Like
from repositories import LikeRepository
from dto.like_dto import LikeAddDTO

like_bp = Blueprint('like_bp', __name__)

@like_bp.route('/', methods=['POST'])
def add_like():
    data = request.get_json()
    like_dto = LikeAddDTO.from_dict(data)

    like = Like(
        users_id=like_dto.users_id,
        posts_id=like_dto.posts_id,
        created_at=datetime.datetime.now()
    )
    
    LikeRepository.add(like)

    return jsonify({'message': 'Like post successfully!'}), 201


@like_bp.route('/<int:likes_id>', methods=['DELETE'])
def delete_like(likes_id):
    like = LikeRepository.get_by_id(likes_id)
    
    if not like:
        return jsonify({'message': 'Like not found!'}), 404
    
    LikeRepository.delete(like)
    
    return jsonify({'message': 'Favorite deleted successfully!'}), 200