from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

def normalize_query_params(city = None,
                          min_stars = 0,
                          max_stars = 5,
                          min_rate = 0,
                          max_rate = 10000,
                          limit = 50,
                          offset = 0, 
                          **data):
    if city:
        return {
            'min_stars': min_stars,
            'max_stars': max_stars,
            'min_rate': min_rate,
            'max_rate': max_rate,
            'city': city,
            'limit': limit,
            'offset': offset
            }
    return {
            'min_stars': min_stars,
            'max_stars': max_stars,
            'min_rate': min_rate,
            'max_rate': max_rate,
            'limit': limit,
            'offset': offset
            }




class Hotels(Resource):
    query_params = reqparse.RequestParser()
    query_params.add_argument('city', type=str, location='args')
    query_params.add_argument('min_stars', type=float, location='args')
    query_params.add_argument('max_stars', type=float, location='args')
    query_params.add_argument('min_rate', type=float, location='args')
    query_params.add_argument('max_rate', type=float, location='args')
    query_params.add_argument('limit', type=float, location='args')
    query_params.add_argument('offset', type=float, location='args')

    def get(self):
        filters = Hotels.query_params.parse_args()

        query = HotelModel.query

        if filters['city']:
            query = query.filter(HotelModel.city.ilike('%' + filters['city'] + '%'))
        if filters['min_stars']:
            query = query.filter(HotelModel.stars >= filters['min_stars'])
        if filters['max_stars']:
            query = query.filter(HotelModel.star <= filters['max_stars'])
        if filters['min_rate']:
            query = query.filter(HotelModel.rate >= filters['min_rate'])
        if filters['max_rate']:
            query = query.filter(HotelModel.rate <= filters['max_rate'])
        if filters['limit']:
            query = query.limit(filters['limit'])
        if filters['offset']:
            query = query.offset(filters['offset'])

        return {'hotels': [hotel.json() for hotel in query]}

class Hotel(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('name', type=str, required=True, help="The field 'name' cannot be left blank.")
    arguments.add_argument('stars', type=float, required=True, help="The field 'stars' cannot be left blank.")
    arguments.add_argument('rate', type=float, required=True, help="The field 'rate' cannot be left blank.")
    arguments.add_argument('city', type=str, required=True, help="The field 'city' cannot be left blank.")
    
    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404 #NOT FOUND

    @jwt_required()
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

    @jwt_required()
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

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An internal error ocurred trying to delete hotel.'}, 500 #INTERNAL ERROR
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404