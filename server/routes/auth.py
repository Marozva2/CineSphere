from flask import Blueprint, jsonify
from flask_bcrypt import Bcrypt
from flask_restful import Api, Resource, reqparse, abort
from flask_jwt_extended import create_access_token, JWTManager
from models import User,db

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()
jwt = JWTManager()
api = Api(auth_bp)

signUp_args = reqparse.RequestParser()
signUp_args.add_argument('firstname',type=str,required=True, help='First Name cannot be blank')
signUp_args.add_argument('lastname',type=str,required=True, help='Last Name cannot be blank')
signUp_args.add_argument("email", type=str, required=True)
signUp_args.add_argument("password", type=str, required=True)
signUp_args.add_argument("confirmPassword", type=str, required=True)

login_args = reqparse.RequestParser()
login_args.add_argument("email", type=str, required=True)
login_args.add_argument("password", type=str, required=True)



class UserRegister(Resource):
    def post(self):
        data = signUp_args.parse_args()
        if data["password"] != data["confirmPassword"]:
            return abort(422, detail="Passwords do not match")
        
        new_user = User( firstname=data.firstname, lastname=data.lastname, email=data.email, password=bcrypt.generate_password_hash(data.password).decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        metadata = {"firstname": new_user.firstname}
        token = create_access_token(identity=new_user.id, additional_claims=metadata)
        return {'detail': f'User {data.firstname} {data.lastname} has been created successfully', 'access token': token}

        
        
class Login(Resource):

    def post(self):
        data = login_args.parse_args()
        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return abort(404, detail="User does not exist")

        if not bcrypt.check_password_hash(user.password, data['password']):
            return abort(403, detail="Incorrect password")
        token = create_access_token(identity=user.id)
        return {"access_token": token, "user_id":user.id,"firstname":user.firstname,"lastname":user.lastname,"email":user.email}
            


api.add_resource(Login, "/login")
api.add_resource(UserRegister, "/register")






