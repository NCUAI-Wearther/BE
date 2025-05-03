from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    posts = db.relationship('Post', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

class StyleTag(db.Model):
    __tablename__ = 'styleTag'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    outfits = db.relationship('Outfit', backref='style', lazy=True)

class OccasionTag(db.Model):
    __tablename__ = 'occasionTag'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    outfits = db.relationship('Outfit', backref='occasion', lazy=True)

class Outfit(db.Model):
    __tablename__ = 'outfits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    styleTag_id = db.Column(db.Integer, db.ForeignKey('styleTag.id'), nullable=False)
    occasionTag_id = db.Column(db.Integer, db.ForeignKey('occasionTag.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    weather_type = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    posts = db.relationship('Post', backref='outfit', lazy=True)
    favorites = db.relationship('Favorite', backref='outfit', lazy=True)
    outfit_items = db.relationship('OutfitItem', backref='outfit', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outfits_id = db.Column(db.Integer, db.ForeignKey('outfits.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    media_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    likes = db.relationship('Like', backref='post', lazy=True)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outfits_id = db.Column(db.Integer, db.ForeignKey('outfits.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Like(db.Model):
    __tablename__ = 'Likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    posts_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class ClothingItem(db.Model):
    __tablename__ = 'clothingItem'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Integer, nullable=False, default=0)
    material = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(30), nullable=True)

    outfit_items = db.relationship('OutfitItem', backref='clothing_item', lazy=True)

class OutfitItem(db.Model):
    __tablename__ = 'outfit_item'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clothingItem_id = db.Column(db.Integer, db.ForeignKey('clothingItem.id'), nullable=False)
    outfits_id = db.Column(db.Integer, db.ForeignKey('outfits.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)