from flask import Blueprint, request, jsonify
from models import Post, Like
from repositories import PostRepository, LikeRepository, UserRepository, OutfitRepository
from schemas import PostSchema, LikeSchema
from routes.user_routes import token_required

post_bp = Blueprint('post_bp', __name__)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
like_schema = LikeSchema()
likes_schema = LikeSchema(many=True)


@post_bp.route('/', methods=['GET'])
def get_all_posts():
    posts = PostRepository.get_all()
    return jsonify(posts_schema.dump(posts)), 200


@post_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = PostRepository.get_by_id(post_id)
    
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    
    return jsonify(post_schema.dump(post)), 200


@post_bp.route('/', methods=['POST'])
def create_post():
    data = request.get_json()

    outfit = OutfitRepository.get_by_id(data['outfits_id'])
    if not outfit:
        return jsonify({'message': 'Outfit not found!'}), 404

    new_post = Post(
        users_id=data['user_id'],
        outfits_id=data['outfits_id'],
        content=data.get('content'),
        media_url=data.get('media_url')
    )
    
    PostRepository.add(new_post)
    
    return jsonify(post_schema.dump(new_post)), 201


@post_bp.route('/<int:post_id>', methods=['PUT'])
def update_post( post_id):
    post = PostRepository.get_by_id(post_id)
    
    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    data = request.get_json()

    if 'content' in data:
        post.content = data['content']
    
    if 'media_url' in data:
        post.media_url = data['media_url']
    
    PostRepository.update()
    
    return jsonify(post_schema.dump(post)), 200


@post_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = PostRepository.get_by_id(post_id)
    
    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    likes = LikeRepository.get_by_post(post_id)
    for like in likes:
        LikeRepository.delete(like)
    
    PostRepository.delete(post)
    
    return jsonify({'message': 'Post deleted successfully!'}), 200


@post_bp.route('/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = PostRepository.get_by_id(post_id)
    
    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    existing_like = LikeRepository.get_by_user_and_post(current_user.id, post_id)
    if existing_like:
        return jsonify({'message': 'Post already liked!'}), 409

    new_like = Like(
        posts_id=post_id,
        users_id=post
    )
    
    LikeRepository.add(new_like)
    
    return jsonify(like_schema.dump(new_like)), 201


# @post_bp.route('/<int:like_id>', methods=['DELETE'])
# def unlike_post(post_id):
#     post = PostRepository.get_by_id(post_id)
    
#     if not post:
#         return jsonify({'message': 'Post not found!'}), 404

#     existing_like = LikeRepository.get_by_user_and_post( post_id)
#     if not existing_like:
#         return jsonify({'message': 'Post not liked!'}), 404
    
#     LikeRepository.delete(existing_like)
    
#     return jsonify({'message': 'Post unliked successfully!'}), 200


# @post_bp.route('/user/<int:user_id>', methods=['GET'])
# def get_user_posts(user_id):
#     user = UserRepository.get_by_id(user_id)
#     if not user:
#         return jsonify({'message': 'User not found!'}), 404
    
#     posts = PostRepository.get_by_user(user_id)
    
#     return jsonify(posts_schema.dump(posts)), 200


# @post_bp.route('/outfit/<int:outfit_id>', methods=['GET'])
# def get_outfit_posts(outfit_id):
#     outfit = OutfitRepository.get_by_id(outfit_id)
#     if not outfit:
#         return jsonify({'message': 'Outfit not found!'}), 404
    
#     posts = PostRepository.get_by_outfit(outfit_id)
    
#     return jsonify(posts_schema.dump(posts)), 200


# @post_bp.route('/<int:post_id>/likes', methods=['GET'])
# def get_post_likes(post_id):
#     post = PostRepository.get_by_id(post_id)
    
#     if not post:
#         return jsonify({'message': 'Post not found!'}), 404
    
#     likes = LikeRepository.get_by_post(post_id)
    
#     return jsonify(likes_schema.dump(likes)), 200