from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_bcrypt import Bcrypt
from flask_restful import Api, Resource, abort, reqparse
from flask_marshmallow import Marshmallow

from models import User, db

user_bp = Blueprint('user_bp', __name__)
ma=Marshmallow(user_bp)
bcrypt = Bcrypt()
api = Api(user_bp)


post_args = reqparse.RequestParser()
post_args.add_argument('firstname', type=str, required=True, help='Fisrt Name is required')
post_args.add_argument('lastname', type=str, required=True, help='Last Name is required')
post_args.add_argument('email', type=str, required=True, help='Email is required')
post_args.add_argument('password', type=str, required=True, help='Password is required')


patch_args = reqparse.RequestParser()
patch_args.add_argument('firstname', type=str)
patch_args.add_argument('lastname', type=str)
patch_args.add_argument('email', type=str)
patch_args.add_argument('password', type=str)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User

userschema = UserSchema()

class Users(Resource):
    def get(self):
        users = User.query.all()
        result = userschema.dump(users, many=True)
        response = make_response(jsonify(result), 200)

        return response

    def post(self):
        data = post_args.parse_args()

        # error handling
        user = User.query.filter_by(email=data.email).first()
        if user:
            abort(409, detail="User with the same email already exists")
        hashed_password = bcrypt.generate_password_hash(data['password'])
        new_user = User(firstname=data['firstname'], lastname=data['lastname'], email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        result = userschema.dump(new_user)
        response = make_response(jsonify(result),201)

        return response


class UserById(Resource):
    def get(self, id):
        single_user = User.query.filter_by(id=id).first()

        if not single_user:
            abort(404, detail=f'user with  id {id} does not exist')

        else:
            result = userschema.dump(single_user)
            response = make_response(jsonify(result), 200)
            return response

    def patch(self, id):
        single_user = User.query.filter_by(id=id).first()

        if not single_user:
            abort(404, detail=f'user with id {id} does not exist')

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is None:
                continue
            setattr( single_user, key, value)
        db.session.commit()
        result = userschema.dump(single_user)
        response = make_response(jsonify(result), 200)

        return response
    
    


api.add_resource(UserById, '/user/<int:id>')
api.add_resource(Users,'/users')

