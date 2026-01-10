import sys
import json
import requests
import Activity 

# Get token from Node.js
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
            
            if response.status_code != 200:
                return {
                    "error": f"Strava API error: {response.status_code}",
                    "details": response.json()
                }
            
            result = response.json()
            
            if not isinstance(result, list):
                return {
                    "error": "Unexpected response from Strava",
                    "response": result
                }

            target_sports = {"Run", "Hike", "TrailRun"}

            # Return dict directly instead of ActivityContainer
            filtered_activities = []
            for activity in result:
                if isinstance(activity, dict) and activity.get("sport_type") in target_sports:
                    filtered_activities.append({
                        "name": activity.get("name"),
                        "type": activity.get("sport_type"),
                        "distance": activity.get("distance"),
                        "elevation_gain": activity.get("total_elevation_gain"),
                        "moving_time": activity.get("moving_time"),
                        "start_date": activity.get("start_date")
                    })

            return filtered_activities  # Return list of dicts, not ActivityContainer
            
        except Exception as e:
            return {
                "error": f"Exception: {str(e)}"
            }

# Create app
app = StravaApp(token)
activities = app.get_walking_activities()

# Return result
if isinstance(activities, dict) and "error" in activities:
    # It's an error dict
    print(json.dumps(activities))
elif isinstance(activities, list):
    # It's a list of activity dicts
    result = {
        "status": "success",
        "message": "Retrieved backpacking activities",
        "total_activities": len(activities),
        "activities": activities
    }
    print(json.dumps(result))
else:
    print(json.dumps({"error": "Unexpected return type"}))