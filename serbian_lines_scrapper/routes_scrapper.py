class BelgradRoute:
    def __init__(self):
        self.route_name = None
        self.description = None
        self.first_station = None
        self.last_station = None
        self.first_st_dep = None
        self.last_st_dep = None

    def get_dict(self):
        scrapped_data = {
            "route_name": self.route_name,
            "route_description": self.description,
            "first_station": {},
            "last_station": {},
        }
        scrapped_data["first_station"]["name"] = self.first_station
        scrapped_data["first_station"]["departures"] = self.first_st_dep
        scrapped_data["last_station"]["name"] = self.last_station
        scrapped_data["last_station"]["departures"] = self.last_st_dep
        return scrapped_data
