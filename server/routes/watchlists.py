from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import Watchlist, db

watchlist_bp = Blueprint('watchlist_bp', __name__)
ma=Marshmallow(watchlist_bp)
api = Api(watchlist_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('user_id', type=int, required=True, help='User ID is required')
post_args.add_argument('movie_id', type=int, required=True, help='Movie ID is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('user_id', type=int)
patch_args.add_argument('movie_id', type=int)

class WatchlistSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Watchlist
        include_fk=True

watchlistschema = WatchlistSchema()

class Watchlists(Resource):
    def get(self):
        watchlists = Watchlist.query.all()
        result = watchlistschema.dump(watchlists, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        new_watchlist = Watchlist(user_id=data['user_id'], movie_id=data['movie_id'])
        db.session.add(new_watchlist)
        db.session.commit()

        result = watchlistschema.dump(new_watchlist)
        response = make_response(jsonify(result), 201)

        return response

class WatchlistById(Resource):
    def get(self, id):
        single_watchlist = Watchlist.query.filter_by(id=id).first()

        if not single_watchlist:
            abort(404, detail=f'Watchlist with {id} does not exist')

        else:
            result = watchlistschema.dump(single_watchlist)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_watchlist = Watchlist.query.filter_by(id=id).first()

        if not single_watchlist:
            abort(404, detail=f'Watchlist with {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr(single_watchlist, key, value)
        db.session.commit()
        result = watchlistschema.dump(single_watchlist)
        response = make_response(jsonify(result), 200)

        return response

    def delete(self, id):
        watchlist = Watchlist.query.filter_by(id=id).first()
        if not watchlist:
            abort(404, detail=f'Watchlist with id {id} does not exist')
        db.session.delete(watchlist)
        db.session.commit()

        response_body = {
            "message": "Watchlist successfully deleted"
        }

        response = make_response(response_body, 200)
        return response

api.add_resource(Watchlists,'/watchlists')
api.add_resource(WatchlistById, '/watchlist/<int:id>')
