import json

class Activity:
    def __init__(self, get_activity_output):
        self.name = get_activity_output.get("name")
        self.id = get_activity_output.get("id") # for debugging
        self.date = get_activity_output.get("start_date")
        self.distance = get_activity_output.get("distance")
        self.elevation = get_activity_output.get("total_elevation_gain")
        self.avg_speed = get_activity_output.get("average_speed")
        self.elapsed_time = get_activity_output.get("elapsed_time")
        self.location = get_activity_output.get("start_latlng")
        self.elev_low = get_activity_output.get("elev_low")
        self.elev_high = get_activity_output.get("elev_high")

    def __str__(self):
        return (f"NAME: {self.name}\n"
                f"Start Location: {self.location}\n"
                f"Distance: {self.distance}\n"
                f"Elevation Gain: {self.elevation}\n"
                f"Avg Speed: {self.avg_speed}\n"
                f"Elapsed Time: {self.elapsed_time}\n"
                f"Elevation Low/High: {self.elev_low} / {self.elev_high}\n\n")

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "start_date": self.date,
            "distance": self.distance,
            "total_elevation_gain": self.elevation,
            "average_speed": self.avg_speed,
            "elapsed_time": self.elapsed_time,
            "start_latlng": self.location,
            "elev_low": self.elev_low,
            "elev_high": self.elev_high
        }

class ActivityContainer:
    def __init__(self, activities):
        self.activities = activities

    def __str__(self):
        return "".join(str(activity) for activity in self.activities)

    # maybe?
    def to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump([activity.to_dict() for activity in self.activities], f, indent=4)

    # Things we need:
    # How long ago they did the activity
    # Distance 
    # Elevation gain
    # Went up to max elevation
    # It took elapsed time
