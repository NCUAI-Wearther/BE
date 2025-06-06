from models import User, Outfit, Post, Favorite, Like, OutfitItem, Cloth, Related

class BaseRepository:
    @staticmethod
    def add(item):
        from app import db
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def update(instance):
        from app import db
        db.session.merge(instance)
        db.session.commit()
    
    @staticmethod
    def delete(item):
        from app import db
        db.session.delete(item)
        db.session.commit()


class UserRepository(BaseRepository):
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


class OutfitRepository(BaseRepository):
    @staticmethod
    def get_by_id(outfit_id):
        return Outfit.query.get(outfit_id)

class PostRepository(BaseRepository):
    @staticmethod
    def get_by_users_id(users_id):
        from models import Post
        return Post.query.filter_by(users_id=users_id).all()

class FavoriteRepository(BaseRepository):
    @staticmethod
    def get_by_users_id(users_id):
        from models import Favorite
        return Favorite.query.filter_by(users_id=users_id).all()
    
    @staticmethod
    def remove_favorite(users_id, outfits_id):
        from models import Favorite
        from app import db
        favorite = Favorite.query.filter_by(users_id=users_id, outfits_id=outfits_id).first()

        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return True
        
        return False

class LikeRepository(BaseRepository):
    def get_by_users_id(users_id):
        from models import Like
        return Like.query.filter_by(users_id=users_id).all()
    
    @staticmethod
    def get_by_posts_id(post_id):
        return Like.query.filter_by(posts_id=post_id).all()


class OutfitItemRepository(BaseRepository):
    @staticmethod
    def get_by_outfits_id(outfits_id):
        from models import OutfitItem
        return OutfitItem.query.filter_by(outfits_id=outfits_id).all()

class ClothRepository(BaseRepository):
    @staticmethod
    def get_by_id(cloth_id):
        return Cloth.query.get(cloth_id)


class RelatedRepository(BaseRepository):
    @staticmethod
    def get_clothes_by_outfit_id(outfit_id):
        return Related.query.filter_by(outfits_id=outfit_id).all()

    @staticmethod
    def get_outfits_by_cloth_id(cloth_id):
        return Related.query.filter_by(clothes_id=cloth_id).all()