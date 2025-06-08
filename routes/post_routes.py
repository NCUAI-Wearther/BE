from collections import Counter
import datetime
import math
from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from models import Favorite, Outfit, db, Post
from repositories import PostRepository
from dto.post_dto import PostCreateDTO, PostViewDTO

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
    decay_weight = 1.0
    like_weight = 1.5
    latest_weight = 3
    limit = 50

    recommended_post_scores = {}  # {post_id: {'post': post, 'score': value}}

    from models import Like
    liked_post_ids = db.session.query(Like.posts_id).filter_by(users_id=users_id).subquery()

    similar_users = db.session.query(Like.users_id)\
        .filter(Like.posts_id.in_(liked_post_ids), Like.users_id != users_id)\
        .distinct().subquery()

    collaborative_post_ids = db.session.query(Like.posts_id)\
        .filter(Like.users_id.in_(similar_users))\
        .filter(~Like.posts_id.in_(liked_post_ids))\
        .distinct().limit(limit).all()

    collaborative_post_ids = [pid[0] for pid in collaborative_post_ids]
    collaborative_posts = db.session.query(Post).filter(Post.id.in_(collaborative_post_ids)).all()

    for post in collaborative_posts:
        like_count = len(post.likes)
        days = (now - post.created_at).days
        decay_score = math.exp(-decay_lambda * days)
        total_score = decay_score * decay_weight + like_count * like_weight
        recommended_post_scores[post.id] = {'post': post, 'score': total_score}

    if len(recommended_post_scores) >= limit:
        sorted_posts = sorted(recommended_post_scores.values(), key=lambda x: x['score'], reverse=True)
        return jsonify({
            'items': [PostViewDTO.from_model(p['post']) for p in sorted_posts[:limit]]
        }), 200

    favorite_outfits = db.session.query(Outfit).join(Favorite).filter(Favorite.users_id == users_id).all()
    if favorite_outfits:
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
            preferred_posts = db.session.query(Post)\
                .filter(Post.outfits_id.in_(preferred_outfit_ids))\
                .filter(~Post.id.in_(recommended_post_scores.keys()))\
                .all()

            for post in preferred_posts:
                like_count = len(post.likes)
                days = (now - post.created_at).days
                decay_score = math.exp(-decay_lambda * days)
                total_score = decay_score * decay_weight + like_count * like_weight
                recommended_post_scores[post.id] = {'post': post, 'score': total_score}

        if len(recommended_post_scores) >= limit:
            sorted_posts = sorted(recommended_post_scores.values(), key=lambda x: x['score'], reverse=True)
            return jsonify({
                'items': [PostViewDTO.from_model(p['post']) for p in sorted_posts[:limit]]
            }), 200

    remaining = limit - len(recommended_post_scores)
    newest_posts = db.session.query(Post)\
        .filter(~Post.id.in_(recommended_post_scores.keys()))\
        .order_by(Post.created_at.desc())\
        .limit(remaining)\
        .all()

    for post in newest_posts:
        total_score = latest_weight
        recommended_post_scores[post.id] = {'post': post, 'score': total_score}

    sorted_posts = sorted(recommended_post_scores.values(), key=lambda x: x['score'], reverse=True)
    return jsonify({
        'items': [PostViewDTO.from_model(p['post']) for p in sorted_posts[:limit]]
    }), 200