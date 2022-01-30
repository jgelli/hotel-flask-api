from flask_restful import Resource, reqparse
from itsdangerous import exc

from models.hotel import HotelModel

class Hotels(Resource):
    def get(self):
        return {'hotels': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('name', type=str, required=True, help="The field 'name' cannot be left blank.")
    arguments.add_argument('stars', type=float, required=True, help="The field 'stars' cannot be left blank.")
    arguments.add_argument('diary', type=float, required=True, help="The field 'diary' cannot be left blank.")
    arguments.add_argument('city', type=str, required=True, help="The field 'city' cannot be left blank.")
    
    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404 #NOT FOUND

    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {'message': f"Hotel id '{hotel_id}' already exists."}, 400 #BAD REQUEST

        data = Hotel.arguments.parse_args()
        hotel = HotelModel(hotel_id, **data)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel.'}, 500 #INTERNAL ERROR
        return hotel.json(), 200 #OK

    def put(self, hotel_id):
        data = Hotel.arguments.parse_args()


        finded_hotel = HotelModel.find_hotel(hotel_id)
        if finded_hotel:
            finded_hotel.update_hotel(**data)
            try:
                finded_hotel.save_hotel()
            except:
                return {'message': 'An internal error ocurred trying to save hotel.'}
            return finded_hotel.json(), 200 #OK

        #if isn't find a hotel, new hotel as created
        hotel = HotelModel(hotel_id, **data)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel.'}, 500 #INTERNAL ERROR
        return hotel.json(), 201 #CREATED

    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An internal error ocurred trying to delete hotel.'}, 500 #INTERNAL ERROR
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404