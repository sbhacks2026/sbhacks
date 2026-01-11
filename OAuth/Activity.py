import json
from datetime import datetime
import requests

class Activity:
    def __init__(self, get_activity_output):
        self.id = get_activity_output.get("id") # for debugging
        self.date = get_activity_output.get("start_date")
        self.sport_type = get_activity_output.get("sport_type")
        self.distance = get_activity_output.get("distance")
        self.elevation = get_activity_output.get("total_elevation_gain")
        self.avg_speed = get_activity_output.get("average_speed")
        self.elapsed_time = get_activity_output.get("elapsed_time")
        self.location = get_activity_output.get("start_latlng")
        self.elev_high = get_activity_output.get("elev_high")

    def __str__(self):
        return (f"Start Location: {self.location}\n"
                f"Distance: {self.distance}\n"
                f"Elevation Gain: {self.elevation}\n"
                f"Avg Speed: {self.avg_speed}\n"
                f"Elapsed Time: {self.elapsed_time}\n"
                f"Elevation Low/High: {self.elev_low} / {self.elev_high}\n\n")

    def to_dict(self):
        return {
            "id": self.id,
            "days_ago": self.get_days_ago(),
            "distance (miles)": int(self.distance / 1609.34),
            "total_elevation_gain (feet)": int(self.elevation * 3.28084),
            "sport_type": self.sport_type,
            "average_speed": self.get_speed_with_units(),
            "elapsed_time": int(self.elapsed_time / 3600),
            "location": self.get_location_name(),
            "max_elevation (feet)": int(self.elev_high * 3.28084)
        }
    
    def get_days_ago(self):
        """Calculate how many days ago the activity was."""
        if self.date is None:
            return "N/A"
        try:
            activity_date = datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ")
            days = (datetime.utcnow() - activity_date).days
            return f"{days} days ago"
        except ValueError:
            return "N/A"

    def get_location_name(self):
        """Get city name from coordinates using BigDataCloud API"""
        if not self.location:
            return "N/A"
        try:
            lat, lng = self.location
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lng}&localityLanguage=en"
            response = requests.get(url).json()
            return response.get('city') or response.get('locality') or "Unknown"
        except Exception:
            return "N/A"

    def get_speed_with_units(self):
        """Returns speed in minutes per mile."""
        if self.avg_speed is None or self.avg_speed == 0:
            return "N/A"
        
        pace = (1609.34 / self.avg_speed) / 60
        minutes = int(pace)
        seconds = int((pace - minutes) * 60)
        return f"{minutes}:{seconds:02d} min/mile"

    def get_elapsed_time_formatted(self):
        """Convert elapsed time from seconds to hours"""
        if self.elapsed_time is None:
            return "N/A"
        hours = self.elapsed_time / 3600
        return int(hours)

class ActivityContainer:
    def __init__(self, activities):
        self.activities = activities

    def __str__(self):
        return "".join(str(activity) for activity in self.activities)

    # maybe?
    def to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump([activity.to_dict() for activity in self.activities], f, indent=4)

    def to_dict(self):
        return [activity.to_dict() for activity in self.activities]

