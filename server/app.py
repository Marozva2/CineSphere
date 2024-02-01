from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from models import db
from routes.movies import movie_bp
from routes.favorites import favorite_bp
from routes.review import review_bp
from routes.users import user_bp, bcrypt
from routes.profile import profile_bp
from routes.auth import auth_bp, jwt
from routes.watchlists import watchlist_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinesphere.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.json.compact = False

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    migrate = Migrate(app, db)

    app.register_blueprint(user_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(watchlist_bp)

    CORS(app)

    return app

app = create_app()