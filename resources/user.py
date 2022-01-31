from flask_restful import Resource, reqparse

from models.user import UserModel

from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp

from blocklist import BLOCKLIST


arguments = reqparse.RequestParser()
arguments.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank.")
arguments.add_argument('password', type=str, required=True, help="The field 'password' cannot be left blank.")

class User(Resource):
    # /user/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'User not found.'}, 404 #NOT FOUND

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {'message': 'An internal error ocurred trying to delete user.'}, 500 #INTERNAL ERROR
            return {'message': 'User deleted.'}
        return {'message': 'User not found.'}, 404

class UserRegister(Resource):
    # /register
    def post(self):
        data = arguments.parse_args()

        if UserModel.find_by_login(data['login']):
            return {'message': f"The login '{data['login']}' already exists."}
        
        user = UserModel(**data)
        user.save_user()
        return {'message': 'User created successfully'}, 201 # CREATED

class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = arguments.parse_args()

        user = UserModel.find_by_login(data['login'])
        
        if user and safe_str_cmp(user.password, data['password']):
            acess_token = create_access_token(identity=user.user_id)
            return {'acess_token': acess_token}, 200
        return {'message': 'The username or password is incorrect.'}, 401

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # JTI -> JWT Token Identifier
        BLOCKLIST.add(jwt_id)
        return {'message': 'Logged out successfully!'}, 200