class HotelModel:
    def __init__(self, hotel_id, name, stars, diary, city):
        self.hotel_id = hotel_id
        self.name = name
        self.stars = stars
        self.diary = diary
        self.city = city

    def json(self):
        return {
            'hotel_id': self.hotel_id,
            'name': self.name,
            'stars': self.stars,
            'diary': self.diary,
            'city': self.city
        }
