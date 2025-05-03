from flask_marshmallow import Marshmallow
from models import User, StyleTag, OccasionTag, Outfit, Post, Favorite, Like, ClothingItem, OutfitItem

ma = Marshmallow()

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    
    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    profile_pic_url = ma.auto_field()
    created_at = ma.auto_field()


class StyleTagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = StyleTag
    
    id = ma.auto_field()
    name = ma.auto_field()


class OccasionTagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OccasionTag
    
    id = ma.auto_field()
    name = ma.auto_field()


class ClothingItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ClothingItem
    
    id = ma.auto_field()
    name = ma.auto_field()
    image_url = ma.auto_field()
    category = ma.auto_field()
    temperature = ma.auto_field()
    material = ma.auto_field()
    color = ma.auto_field()


class OutfitItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OutfitItem
    
    id = ma.auto_field()
    clothingItem_id = ma.auto_field()
    outfits_id = ma.auto_field()
    category = ma.auto_field()
    
    clothing_item = ma.Nested(ClothingItemSchema)


class OutfitSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Outfit
    
    id = ma.auto_field()
    styleTag_id = ma.auto_field()
    occasionTag_id = ma.auto_field()
    name = ma.auto_field()
    weather_type = ma.auto_field()
    created_at = ma.auto_field()
    
    style = ma.Nested(StyleTagSchema)
    occasion = ma.Nested(OccasionTagSchema)
    outfit_items = ma.Nested(OutfitItemSchema, many=True)


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
    
    id = ma.auto_field()
    users_id = ma.auto_field()
    outfits_id = ma.auto_field()
    content = ma.auto_field()
    media_url = ma.auto_field()
    created_at = ma.auto_field()
    
    author = ma.Nested(UserSchema)
    outfit = ma.Nested(OutfitSchema)
    likes_count = ma.Function(lambda obj: len(obj.likes))


class FavoriteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Favorite
    
    id = ma.auto_field()
    users_id = ma.auto_field()
    outfits_id = ma.auto_field()
    created_at = ma.auto_field()
    
    outfit = ma.Nested(OutfitSchema)


class LikeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Like
    
    id = ma.auto_field()
    posts_id = ma.auto_field()
    users_id = ma.auto_field()
    created_at = ma.auto_field()
    
    post = ma.Nested(PostSchema)

class LocationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Like
    
    id = ma.auto_field()
    posts_id = ma.auto_field()
    users_id = ma.auto_field()
    created_at = ma.auto_field()