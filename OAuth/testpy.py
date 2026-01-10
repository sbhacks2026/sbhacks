import sys
import json
import requests
import Activity 

# Get token from Node.js
token = sys.argv[1] if len(sys.argv) > 1 else "NO TOKEN RECEIVED"

if token == "NO TOKEN RECEIVED":
    print(json.dumps({"error": "No token provided"}))
    sys.exit(1)

class StravaApp:
    def __init__(self, token: str):
        self.token = token

    def get_walking_activities(self):
        request_url = 'https://www.strava.com/api/v3/athlete/activities'
        header = {"Authorization": "Bearer " + self.token}

        result = requests.get(request_url, headers=header).json()

        target_sports = {"Run", "Hike", "TrailRun"}

        filtered_activities = [
            Activity.Activity(activity) for activity in result
            if activity.get("sport_type") in target_sports
        ]

        return Activity.ActivityContainer(filtered_activities)

# Create app with the user's token
app = StravaApp(token)
activities = app.get_walking_activities()

# Convert to dictionary for JSON output
result = {
    "status": "success",
    "message": "Retrieved backpacking activities",
    "activities": activities.to_dict() if hasattr(activities, 'to_dict') else str(activities)
}

print(json.dumps(result))