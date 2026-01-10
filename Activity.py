import json

class Activity:
    def __init__(self, get_activity_output):
        self.name = get_activity_output.get("name")
        self.id = get_activity_output.get("id") # for debugging
        self.date = get_activity_output.get("start_date")
        self.sport_type = get_activity_output.get("sport_type")
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
            "name ": self.name,
            "id": self.id,
            "start_date": self.date,
            "distance (meters)": self.distance,
            "total_elevation_gain (meters)": self.elevation,
            "sport_type": self.sport_type,
            "average_speed": self.get_speed_with_units(),
            "elapsed_time (sec)": self.elapsed_time,
            "start_latlng": self.location,
            "elev_low (meters)": self.elev_low,
            "elev_high (meters)": self.elev_high
        }
    
    def get_speed_with_units(self):
        """Returns speed with appropriate units based on sport type."""
        if self.avg_speed is None or self.avg_speed == 0:
            return "N/A"

        def convert_to_min_per_mile():
            """Convert m/s to min/mile (pace)"""
            miles_per_second = self.avg_speed / 1609.34
            minutes_per_mile = 1 / (miles_per_second * 60) if miles_per_second > 0 else 0
            mins = int(minutes_per_mile)
            secs = int((minutes_per_mile - mins) * 60)
            return f"{mins}:{secs:02d} min/mile"

        def convert_to_mph():
            """Convert m/s to mph"""
            mph = self.avg_speed * 2.23694
            return f"{mph:.2f} mph"

        # Return appropriate unit based on sport type
        if self.sport_type == "Run":
            return convert_to_min_per_mile()
        elif self.sport_type == "Hike":
            return convert_to_min_per_mile()
        elif self.sport_type == "TrailRun":
            return convert_to_mph()
        else:
            # Default fallback for other sport types
            return f"{self.avg_speed:.2f} m/s"


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
