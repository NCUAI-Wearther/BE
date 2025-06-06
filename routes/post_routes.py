import datetime
from flask import Blueprint, current_app, request, jsonify

from models import Post
from repositories import PostRepository
from dto.post_dto import PostCreateDTO, PostUpdateDTO, PostViewDTO

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/', methods=['POST'])
def create_post():
    data = request.get_json()
    post = PostCreateDTO.from_dict(data)

    new_Post = Post(
        users_id=post.users_id,
        outfits_id=post.outfits_id,
        content=post.content,
        media_url=post.media_url,
        created_at = datetime.datetime.now()
    )

    PostRepository.add(new_Post)

    return jsonify({'message': 'Post created successfully!'}), 201