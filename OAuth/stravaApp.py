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

        response = requests.get(request_url, headers=header)
        if response.status_code != 200:
            return Activity.ActivityContainer([])

        result = response.json()

        target_sports = {"Run", "Hike", "TrailRun"} # filter to only backpacking related things

        filtered_activities = [
            Activity.Activity(activity) for activity in result
            if activity.get("sport_type") in target_sports
        ]

        return Activity.ActivityContainer(filtered_activities)
    
token = sys.argv[1] if len(sys.argv) > 1 else None
app = StravaApp(token)
activities = app.get_walking_activities()

if hasattr(activities, 'to_dict'):
    output = activities.to_dict()
else:
    output = {"error": "Could not convert activities to dict"}

print(json.dumps(output))
