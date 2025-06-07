from collections import Counter
import datetime
import math
from flask import Blueprint, current_app, request, jsonify
from sqlalchemy import or_

from models import Favorite, Outfit, db, Post
from repositories import FavoriteRepository, PostRepository
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

@post_bp.route('/<int:users_id>', methods=['GET'])
def get_posts(users_id):
    now = datetime.datetime.now()
    decay_lambda = 0.01
    latest_weight = 3

    latest_posts = db.session.query(Post).order_by(Post.created_at.desc()).limit(30).all()

    if not latest_posts:
        return jsonify({'message': 'No posts found.', 'posts': []}), 200

    favorite_outfits = db.session.query(Outfit).join(Favorite).filter(Favorite.users_id == users_id).all()

    if not favorite_outfits:
        return jsonify({
            'items': [PostViewDTO.from_model(post) for post in latest_posts]
        }), 200

    style_counter = Counter(o.style_tag for o in favorite_outfits if o.style_tag)
    occasion_counter = Counter(o.occasion_tag for o in favorite_outfits if o.occasion_tag)

    top_styles = [style for style, _ in style_counter.most_common(3)]
    top_occasions = [occasion for occasion, _ in occasion_counter.most_common(3)]

    preferred_outfits = db.session.query(Outfit).filter(
        or_(
            Outfit.style_tag.in_(top_styles),
            Outfit.occasion_tag.in_(top_occasions)
        )
    ).all()

    preferred_outfit_ids = [o.id for o in preferred_outfits]

    if preferred_outfit_ids:
        preferred_posts = db.session.query(Post).filter(Post.outfits_id.in_(preferred_outfit_ids)).order_by(Post.created_at.desc()).all()
    else:
        preferred_posts = []

    candidate_scores = {}
    for post in latest_posts:
        candidate_scores[post.id] = {
            'post': post,
            'score': latest_weight
        }

    for post in preferred_posts:
        days = (now - post.created_at).days
        decay_score = math.exp(-decay_lambda * days)

        if post.id in candidate_scores:
            candidate_scores[post.id]['score'] += decay_score
        else:
            candidate_scores[post.id] = {
                'post': post,
                'score': decay_score
            }

    sorted_posts = sorted(candidate_scores.values(), key=lambda x: x['score'], reverse=True)
    top_posts = [item['post'] for item in sorted_posts[:30]]

    return jsonify({
        'items': [PostViewDTO.from_model(post) for post in top_posts]
    }), 200