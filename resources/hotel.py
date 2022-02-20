from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

def normalize_path_params(city = None,
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

#path /hotels?city=washington&min_stars=4
path_params = reqparse.RequestParser()
path_params.add_argument('city', type=str)
path_params.add_argument('min_stars', type=float)
path_params.add_argument('max_stars', type=float)
path_params.add_argument('min_rate', type=float)
path_params.add_argument('max_rate', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)


class Hotels(Resource):
    def get(self):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        data = path_params.parse_args()
        valid_data = {key:data[key] for key in data if data[key] is not None}
        parameters = normalize_path_params(**valid_data)

        if not parameters.get('city'):
            query = "SELECT * FROM hotels \
                     WHERE (stars > ? AND stars < ?) \
                     AND (rate > ? AND rate < ?) \
                     LIMIT ? OFFSET ?"
            tuple_parameters = tuple([parameters[key] for key in parameters])
            result = cursor.execute(query, tuple_parameters) #"SELECT * FROM hotels WHERE (stars > min_stars AND stars < max_stars) AND (rate > ? min_rate AND rate < max_rate) LIMIT limit OFFSET offset"
        else:
            query = "SELECT * FROM hotels \
                     WHERE (stars >= ? AND stars <= ?) \
                     AND (rate >= ? AND rate <= ?) \
                     AND city = ? LIMIT ? OFFSET ?"
            tuple_parameters = tuple([parameters[key] for key in parameters])
            result = cursor.execute(query, tuple_parameters) #"SELECT * FROM hotels WHERE (stars > min_stars AND stars < max_stars) AND (rate > ? min_rate AND rate < max_rate) AND city = city LIMIT limit OFFSET offset"

        hotels = []
        for line in result:
            hotels.append({
                'hotel_id': line[0], # self.hotel_id
                'name': line[1], # self.name
                'stars': line[2], # self.stars
                'rate': line[3], # self.rate
                'city': line[4] # self.city
            })

        return {'hotels': hotels}

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