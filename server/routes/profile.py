from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import Profile, db

profile_bp = Blueprint('profile_bp', __name__)
ma=Marshmallow(profile_bp)
api = Api(profile_bp)


post_args = reqparse.RequestParser()
post_args.add_argument('user_id', type=int, required=True, help='Profile user_id is required')
post_args.add_argument('firstname', type=str, required=True, help='Profile first name is required')
post_args.add_argument('lastname', type=str, required=True, help='Profile last name is required')
post_args.add_argument('location', type=str, required=True, help='Profile location is required')


patch_args = reqparse.RequestParser()
patch_args.add_argument('user_id', type=int)
patch_args.add_argument('firstname', type=str)
patch_args.add_argument('lastname', type=str)
patch_args.add_argument('location', type=str)



class ProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        include_fk=True

profileschema = ProfileSchema()

class Profiles(Resource):
    def get(self):
        products = Profile.query.all()
        result = profileschema.dump(products, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        # error handling
        profile = Profile.query.filter_by(firstname=data['firstname'], lastname=data['lastname']).first()
        if profile:
            abort(409, detail="Productname with the same profile already exists")

        new_profile = Profile(firstname=data['firstname'], lastname=data['lastname'], location=data['location'])
        db.session.add(new_profile)
        db.session.commit()

        result = profileschema.dump(new_profile)
        response = make_response(jsonify(result),201)

        return response


class ProfileById(Resource):
    def get(self, id):
        single_profile = Profile.query.filter_by(id=id).first()

        if not single_profile:
            abort(404, detail=f'Profile with {id} does not exist')

        else:
            result = profileschema.dump(single_profile)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_profile = Profile.query.filter_by(id=id).first()

        if not single_profile:
            abort(404, detail=f'Profile with {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr( single_profile, key, value)
        db.session.commit()
        result = profileschema.dump(single_profile)
        response = make_response(jsonify(result), 200)

        return response

        

    def delete(self, id):
        profile = Profile.query.filter_by(id=id).first()
        if not profile:
            abort(404, detail=f'Profile with id {id} does not exist')
        db.session.delete(profile)
        db.session.commit()

        response_body = {
            "message": "Profile successfully deleted"
        }

        response = make_response(response_body, 200)
        return response



api.add_resource(ProfileById, '/profile/<int:id>')
api.add_resource(Profiles,'/profiles')

