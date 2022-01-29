from flask_restful import Resource, reqparse

from models.hotel import HotelModel

hotels = [
    {
        'hotel_id': 'alpha',
        'name': 'Alpha Hotel',
        'stars': 4.3,
        'diary': 380.50,
        'city': 'New York'
    },
    {
        'hotel_id': 'bravo',
        'name': 'Bravo Hotel',
        'stars': 4.4,
        'diary': 420.34,
        'city': 'Los Angeles'
    },
    {
        'hotel_id': 'charlie',
        'name': 'Charlie Hotel',
        'stars': 3.9,
        'diary': 320.20,
        'city': 'Orlando'
    }
]


class Hotels(Resource):
    def get(self):
        return {'hotels': hotels}

class Hotel(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('name')
    arguments.add_argument('stars')
    arguments.add_argument('diary')
    arguments.add_argument('city')

    def find_hotel(hotel_id):
        for hotel in hotels:
            if hotel['hotel_id'] == hotel_id:
                return hotel
        return None
    
    def get(self, hotel_id):
        hotel = Hotel.find_hotel(hotel_id)
        if hotel:
            return hotel
        return {'message': 'Hotel not found.'}, 404 #NOT FOUND

    def post(self, hotel_id):
        data = Hotel.arguments.parse_args()
        object_hotel = HotelModel(hotel_id, **data)
        new_hotel = object_hotel.json()
        hotels.append(new_hotel)
        return new_hotel, 200 #OK

    def put(self, hotel_id):
        data = Hotel.arguments.parse_args()
        object_hotel = HotelModel(hotel_id, **data)
        new_hotel = object_hotel.json()

        hotel = Hotel.find_hotel(hotel_id)
        if hotel:
            hotel.update(new_hotel)
            return new_hotel, 200 #OK
        hotels.append(new_hotel)
        return new_hotel, 201 #CREATED

    def delete(self, hotel_id):
        global hotels
        hotels = [hotel for hotel in hotels if hotel['hotel_id'] != hotel_id]
        return {'message': 'Hotel deleted.'}