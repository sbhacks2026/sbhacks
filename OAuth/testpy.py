import sys
import json
import requests
import Activity 

# Get token from Node.js (NOT hardcoded!)
if len(sys.argv) > 1:
    token = sys.argv[1]
else:
    print(json.dumps({"error": "No token provided"}))
    sys.exit(1)

class StravaApp:
    def __init__(self, token: str):
        self.token = token

    def get_walking_activities(self):
        request_url = 'https://www.strava.com/api/v3/athlete/activities'
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(request_url, headers=headers)
            
            # Check if request was successful
            if response.status_code != 200:
                return {
                    "error": f"Strava API error: {response.status_code}",
                    "details": response.json()
                }
            
            result = response.json()
            
            # Check if result is a list
            if not isinstance(result, list):
                return {
                    "error": "Unexpected response from Strava",
                    "response": result
                }

            target_sports = {"Run", "Hike", "TrailRun"}

            filtered_activities = []
            for activity in result:
                if isinstance(activity, dict) and activity.get("sport_type") in target_sports:
                    filtered_activities.append(Activity.Activity(activity))

            return Activity.ActivityContainer(filtered_activities)
            
        except Exception as e:
            return {
                "error": f"Exception: {str(e)}"
            }

# Create app
app = StravaApp(token)
activities = app.get_walking_activities()

# Return result
if isinstance(activities, dict):
    # It's an error dict
    print(json.dumps(activities))
else:
    # It's an ActivityContainer
    result = {
        "status": "success",
        "message": "Retrieved backpacking activities",
        "activities": activities.to_dict()
    }
    print(json.dumps(result))