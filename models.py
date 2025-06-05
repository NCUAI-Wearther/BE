from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(5))
    birthday = Column(Date)
    created_at = Column(DateTime, nullable=False)

    posts = relationship("Post", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    likes = relationship("Like", back_populates="user")
    user_preferences = relationship("UserPreference", back_populates="user")

class Outfit(db.Model):
    __tablename__ = 'outfits'

    id = Column(Integer, primary_key=True)
    isRain = Column(Boolean, nullable=False, default=False)
    weather_condition = Column(String(20), nullable=False)
    style_tag = Column(String(30), nullable=False, default='無')
    occasion_tag = Column(String(30), nullable=False, default='無')
    image_url = Column(String(200))
    created_at = Column(DateTime, nullable=False)

    posts = relationship("Post", back_populates="outfit")
    favorites = relationship("Favorite", back_populates="outfit")
    outfit_items = relationship("OutfitItem", back_populates="outfit")
    related = relationship("Related", back_populates="outfit")

class Post(db.Model):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    outfits_id = Column(Integer, ForeignKey('outfits.id'), nullable=False)
    content = Column(Text)
    media_url = Column(String(255))
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="posts")
    outfit = relationship("Outfit", back_populates="posts")
    likes = relationship("Like", back_populates="post")

class Favorite(db.Model):
    __tablename__ = 'favorites'

    users_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    outfits_id = Column(Integer, ForeignKey('outfits.id'), primary_key=True)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="favorites")
    outfit = relationship("Outfit", back_populates="favorites")

class Like(db.Model):
    __tablename__ = 'likes'

    users_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    posts_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class OutfitItem(db.Model):
    __tablename__ = 'outfit_item'

    id = Column(Integer, primary_key=True)
    outfits_id = Column(Integer, ForeignKey('outfits.id'), nullable=False)
    category = Column(String(30), nullable=False)
    name = Column(String(200), nullable=False)

    outfit = relationship("Outfit", back_populates="outfit_items")

class Cloth(db.Model):
    __tablename__ = 'clothes'

    id = Column(Integer, primary_key=True)
    brand = Column(String(45), nullable=False)
    category = Column(String(30), nullable=False)
    name = Column(String(200), nullable=False)
    product_pic_url = Column(String(255), nullable=False)
    link_url = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)

    related = relationship("Related", back_populates="cloth")

class Related(db.Model):
    __tablename__ = 'related'

    clothes_id = Column(Integer, ForeignKey('clothes.id'), primary_key=True)
    outfits_id = Column(Integer, ForeignKey('outfits.id'), primary_key=True)

    cloth = relationship("Cloth", back_populates="related")
    outfit = relationship("Outfit", back_populates="related")

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    style_tag = Column(String(30), nullable=False, default='無')
    occasion_tag = Column(String(30), nullable=False, default='無')
    preference_score = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="user_preferences")