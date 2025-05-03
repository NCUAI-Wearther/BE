from models import db, User, StyleTag, OccasionTag, Outfit, Post, Favorite, Like, ClothingItem, OutfitItem

class BaseRepository:
    @staticmethod
    def add(item):
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def update():
        db.session.commit()
    
    @staticmethod
    def delete(item):
        db.session.delete(item)
        db.session.commit()


class UserRepository(BaseRepository):
    @staticmethod
    def get_all():
        return User.query.all()
    
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


class StyleTagRepository(BaseRepository):
    @staticmethod
    def get_all():
        return StyleTag.query.all()
    
    @staticmethod
    def get_by_id(style_id):
        return StyleTag.query.get(style_id)
    
    @staticmethod
    def get_by_name(name):
        return StyleTag.query.filter_by(name=name).first()


class OccasionTagRepository(BaseRepository):
    @staticmethod
    def get_all():
        return OccasionTag.query.all()
    
    @staticmethod
    def get_by_id(occasion_id):
        return OccasionTag.query.get(occasion_id)
    
    @staticmethod
    def get_by_name(name):
        return OccasionTag.query.filter_by(name=name).first()


class OutfitRepository(BaseRepository):
    @staticmethod
    def get_all():
        return Outfit.query.all()
    
    @staticmethod
    def get_by_id(outfit_id):
        return Outfit.query.get(outfit_id)
    
    @staticmethod
    def get_by_weather(weather_type):
        return Outfit.query.filter_by(weather_type=weather_type).all()
    
    @staticmethod
    def get_by_style(style_id):
        return Outfit.query.filter_by(styleTag_id=style_id).all()
    
    @staticmethod
    def get_by_occasion(occasion_id):
        return Outfit.query.filter_by(occasionTag_id=occasion_id).all()


class PostRepository(BaseRepository):
    @staticmethod
    def get_all():
        return Post.query.all()
    
    @staticmethod
    def get_by_id(post_id):
        return Post.query.get(post_id)
    
    @staticmethod
    def get_by_user(user_id):
        return Post.query.filter_by(users_id=user_id).all()
    
    @staticmethod
    def get_by_outfit(outfit_id):
        return Post.query.filter_by(outfits_id=outfit_id).all()


class FavoriteRepository(BaseRepository):
    @staticmethod
    def get_all():
        return Favorite.query.all()
    
    @staticmethod
    def get_by_id(favorite_id):
        return Favorite.query.get(favorite_id)
    
    @staticmethod
    def get_by_user(user_id):
        return Favorite.query.filter_by(users_id=user_id).all()
    
    @staticmethod
    def get_by_outfit(outfit_id):
        return Favorite.query.filter_by(outfits_id=outfit_id).all()
    
    @staticmethod
    def get_by_user_and_outfit(user_id, outfit_id):
        return Favorite.query.filter_by(users_id=user_id, outfits_id=outfit_id).first()


class LikeRepository(BaseRepository):
    @staticmethod
    def get_all():
        return Like.query.all()
    
    @staticmethod
    def get_by_id(like_id):
        return Like.query.get(like_id)
    
    @staticmethod
    def get_by_user(user_id):
        return Like.query.filter_by(users_id=user_id).all()
    
    @staticmethod
    def get_by_post(post_id):
        return Like.query.filter_by(posts_id=post_id).all()
    
    @staticmethod
    def get_by_user_and_post(user_id, post_id):
        return Like.query.filter_by(users_id=user_id, posts_id=post_id).first()


class ClothingItemRepository(BaseRepository):
    @staticmethod
    def get_all():
        return ClothingItem.query.all()
    
    @staticmethod
    def get_by_id(item_id):
        return ClothingItem.query.get(item_id)
    
    @staticmethod
    def get_by_category(category):
        return ClothingItem.query.filter_by(category=category).all()
    
    @staticmethod
    def get_by_temperature(temp):
        return ClothingItem.query.filter_by(temperature=temp).all()


class OutfitItemRepository(BaseRepository):
    @staticmethod
    def get_all():
        return OutfitItem.query.all()
    
    @staticmethod
    def get_by_id(outfit_item_id):
        return OutfitItem.query.get(outfit_item_id)
    
    @staticmethod
    def get_by_outfit(outfit_id):
        return OutfitItem.query.filter_by(outfits_id=outfit_id).all()
    
    @staticmethod
    def get_by_clothing_item(clothing_item_id):
        return OutfitItem.query.filter_by(clothingItem_id=clothing_item_id).all()