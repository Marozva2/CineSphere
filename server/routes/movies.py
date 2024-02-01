from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import Movie, db

movie_bp = Blueprint('movie_bp', __name__)
ma=Marshmallow(movie_bp)
api = Api(movie_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('title', type=str, required=True, help='Movie title is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('title', type=str)

class MovieSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Movie
        include_fk=True

movieschema = MovieSchema()

class Movies(Resource):
    def get(self):
        movies = Movie.query.all()
        result = movieschema.dump(movies, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        # error handling
        movie = Movie.query.filter_by(title=data['title']).first()
        if movie:
            abort(409, detail="Movie with the same title already exists")

        new_movie = Movie(title=data['title'])
        db.session.add(new_movie)
        db.session.commit()

        result = movieschema.dump(new_movie)
        response = make_response(jsonify(result), 201)

        return response

class MovieById(Resource):
    def get(self, id):
        single_movie = Movie.query.filter_by(id=id).first()

        if not single_movie:
            abort(404, detail=f'Movie with {id} does not exist')

        else:
            result = movieschema.dump(single_movie)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_movie = Movie.query.filter_by(id=id).first()

        if not single_movie:
            abort(404, detail=f'Movie with {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr(single_movie, key, value)
        db.session.commit()
        result = movieschema.dump(single_movie)
        response = make_response(jsonify(result), 200)

        return response

    def delete(self, id):
        movie = Movie.query.filter_by(id=id).first()
        if not movie:
            abort(404, detail=f'Movie with id {id} does not exist')
        db.session.delete(movie)
        db.session.commit()

        response_body = {
            "message": "Movie successfully deleted"
        }

        response = make_response(response_body, 200)
        return response

api.add_resource(Movies,'/movies')
api.add_resource(MovieById, '/movie/<int:id>')
