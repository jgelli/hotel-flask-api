from flask import Flask, jsonify
from flask_restful import Api

from resources.hotel import Hotels, Hotel
from resources.user import User, UserRegister, UserLogin, UserLogout 
from flask_jwt_extended import JWTManager

from blocklist import BLOCKLIST

from settings import JWT_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_BLACKLIST_ENABLED'] = True
api = Api(app)
jwt = JWTManager(app)

@app.before_first_request
def create_database():
    database.create_all()

@jwt.token_in_blocklist_loader
def verify_blocklist(self, token):
    return token['jti'] in BLOCKLIST

@jwt.revoked_token_loader
def invalided_acess_token(jwt_header, jwt_payload):
    return jsonify({'message': 'You have been logged out.'}), 401 # unauthorized

#Hotel
api.add_resource(Hotels, '/hotels')
api.add_resource(Hotel, '/hotels/<string:hotel_id>')

#User
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    from sql_alchemy import database
    database.init_app(app)
    app.run(debug=True)