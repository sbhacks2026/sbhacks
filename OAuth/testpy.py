import sys
import json
import requests
import Activity 

def get_token():
    auth_url = "https://www.strava.com/oauth/token"
    data = {
        'client_id' : "131194",
        'client_secret' : "7887ba703fc006c6005393540d018817b8a2151c",
        'grant_type' : 'refresh_token',
        'refresh_token' : '743893e4a18f830aa6b837a1b7492b766d54f0a7'
    }

    #request
    auth_result = requests.post(auth_url, data=data).json()
    access_token = auth_result['access_token']
    return access_token

token = sys.argv[1] if len(sys.argv) > 1 else "NO TOKEN RECEIVED"

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
    
    
app = StravaApp(token)
activities = app.get_walking_activities()
#print(activities)
activities.to_json('strava_data.json')

# result = {
#     "status": "success",
#     "message": "Received access token!",
#     "token": access_token,
#     "token_length": len(access_token),
#     "first_10_chars": access_token[:10] if access_token != "NO TOKEN RECEIVED" else "N/A"
# }

print(json.dumps(activities))