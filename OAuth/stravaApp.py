import json
import requests
import Activity 
import sys

class StravaApp:
    def __init__(self, token : str):
        self.token = token

    def get_walking_activities(self):
        request_url = f'https://www.strava.com/api/v3/athlete/activities'
        header = {"Authorization" : "Bearer " + self.token}

        result = requests.get(request_url, headers=header).json()

        target_sports = {"Run", "Hike", "TrailRun"} # filter to only backpacking related things

        filtered_activities = [
            Activity.Activity(activity) for activity in result
            if activity.get("sport_type") in target_sports
        ]

        return Activity.ActivityContainer(filtered_activities)
    
token = sys.argv[1] if len(sys.argv) > 1 else None
app = StravaApp(token)
activities = app.get_walking_activities()
activities.to_json('strava_data.json')