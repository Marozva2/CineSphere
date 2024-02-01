from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import Review, db

review_bp = Blueprint('review_bp', __name__)
ma=Marshmallow(review_bp)
api = Api(review_bp)


post_args = reqparse.RequestParser()
post_args.add_argument('product_id', type=int, required=True, help='Review product_id is required')
post_args.add_argument('user_id', type=int, required=True, help='Review user_id is required')
post_args.add_argument('rating', type=int, required=True, help='Review rating is required')
post_args.add_argument('content', type=str, required=True, help='Review content is required')


patch_args = reqparse.RequestParser()
patch_args.add_argument('product_id', type=int)
patch_args.add_argument('user_id', type=int)
patch_args.add_argument('rating', type=int)
patch_args.add_argument('content', type=str)



class ReviewSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        include_fk=True

reviewschema = ReviewSchema()

class Reviews(Resource):
    def get(self):
        review = Review.query.all()
        result = reviewschema.dump(review, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        # error handling
        # review = Review.query.filter_by(description=data.description).first()
        # if review:
        #     abort(409, detail="Productname with the same description already exists")

        new_review = Review(product_id=data['product_id'], user_id=data['user_id'], rating=data['rating'], content=data['content'])
        db.session.add(new_review)
        db.session.commit()

        result = reviewschema.dump(new_review)
        response = make_response(jsonify(result),201)

        return response


class ReviewById(Resource):
    def get(self, id):
        single_review = Review.query.filter_by(id=id).first()

        if not single_review:
            abort(404, detail=f'Review with {id} does not exist')

        else:
            result = reviewschema.dump(single_review)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_review = Review.query.filter_by(id=id).first()

        if not single_review:
            abort(404, detail=f'Review with {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr( single_review, key, value)
        db.session.commit()
        result = reviewschema.dump(single_review)
        response = make_response(jsonify(result), 200)

        return response

        

    def delete(self, id):
        review = Review.query.filter_by(id=id).first()
        if not review:
            abort(404, detail=f'Review with id {id} does not exist')
        db.session.delete(review)
        db.session.commit()

        response_body = {
            "message": "Review successfully deleted"
        }

        response = make_response(response_body, 200)
        return response


api.add_resource(Reviews,'/reviews')
api.add_resource(ReviewById, '/review/<int:id>')


