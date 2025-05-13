from flask import Flask
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}}, supports_credentials=True)

    with app.app_context():
        db.create_all()

    from routes.user_routes import user_bp
    from routes.outfit_routes import outfit_bp
    from routes.post_routes import post_bp
    from routes.favorite_routes import favorite_bp
    from routes.like_routes import like_bp
    from routes.clothes_routes import clothes_bp
    from routes.tryon_routes import tryon_bp
    from routes.weather_routes import weather_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(outfit_bp, url_prefix='/api/outfits')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(favorite_bp, url_prefix='/api/favorites')
    app.register_blueprint(like_bp, url_prefix='/api/likes')
    app.register_blueprint(clothes_bp, url_prefix='/api/clothes')
    app.register_blueprint(tryon_bp, url_prefix='/api/tryons')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')

    return app