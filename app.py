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
    from routes.clothing_routes import clothing_bp
    from routes.cwa_routes import cwa_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(outfit_bp, url_prefix='/api/outfits')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(clothing_bp, url_prefix='/api/clothing')
    app.register_blueprint(cwa_bp, url_prefix='/api/weather')
    
    return app