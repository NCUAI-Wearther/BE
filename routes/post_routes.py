import datetime
from flask import Blueprint, current_app, request, jsonify

from models import Post
from repositories import PostRepository
from dto.post_dto import PostCreateDTO, PostUpdateDTO, PostViewDTO

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/', methods=['GET'])
def get_all():
    posts = PostRepository.getAll()
    if posts == None:
        return jsonify({'message': 'Post not found!', 'posts':[]}), 404

    response = []
    for post in posts:
        response.append(PostViewDTO.from_model(post))
        # ADD outfit, Like, favorite
    
    return jsonify({'posts':posts}), 200


@post_bp.route('/', methods=['POST'])
def create_post():
    data = request.get_json()
    post = PostCreateDTO.from_dict(data)

    new_Post = Post(
        users_id=post.users_id,
        outfits_id=post.outfits_id,
        content=post.content,
        media_url=post.media_url,
        created_at = datetime.datetime.now
    )
    
    PostRepository.add(new_Post)

    return jsonify({'message': 'Post created successfully!'}), 201

@post_bp.route('/<int:posts_id>', methods=['PUT'])
def update_post(posts_id):
    data = request.get_json()
    post_dto = PostUpdateDTO.from_dict(data)
    post = PostRepository.get_by_id(posts_id)

    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    post.content = post_dto.content
    post.content = post_dto.content

    PostRepository.update(post)

    return jsonify({'message': 'Post updated successfully!'}), 200

@post_bp.route('/<int:posts_id>', methods=['DELETE'])
def delete_post(posts_id):
    post = PostRepository.get_by_id(posts_id)
    
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    
    PostRepository.delete(post)
    
    return jsonify({'message': 'Post deleted successfully!'}), 200