from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import Favorite, db

favorite_bp = Blueprint('favorite_bp', __name__)
ma=Marshmallow(favorite_bp)
api = Api(favorite_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('user_id', type=int, required=True, help='User ID is required')
post_args.add_argument('movie_id', type=int, required=True, help='Movie ID is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('user_id', type=int)
patch_args.add_argument('movie_id', type=int)

class FavoriteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Favorite
        include_fk=True

favoriteschema = FavoriteSchema()

class Favorites(Resource):
    def get(self):
        favorites = Favorite.query.all()
        result = favoriteschema.dump(favorites, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        new_favorite = Favorite(user_id=data['user_id'], movie_id=data['movie_id'])
        db.session.add(new_favorite)
        db.session.commit()

        result = favoriteschema.dump(new_favorite)
        response = make_response(jsonify(result), 201)

        return response

class FavoriteById(Resource):
    def get(self, id):
        single_favorite = Favorite.query.filter_by(id=id).first()

        if not single_favorite:
            abort(404, detail=f'Favorite with {id} does not exist')

        else:
            result = favoriteschema.dump(single_favorite)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_favorite = Favorite.query.filter_by(id=id).first()

        if not single_favorite:
            abort(404, detail=f'Favorite with {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr(single_favorite, key, value)
        db.session.commit()
        result = favoriteschema.dump(single_favorite)
        response = make_response(jsonify(result), 200)

        return response

    def delete(self, id):
        favorite = Favorite.query.filter_by(id=id).first()
        if not favorite:
            abort(404, detail=f'Favorite with id {id} does not exist')
        db.session.delete(favorite)
        db.session.commit()

        response_body = {
            "message": "Favorite successfully deleted"
        }

        response = make_response(response_body, 200)
        return response

api.add_resource(Favorites,'/favorites')
api.add_resource(FavoriteById, '/favorite/<int:id>')
