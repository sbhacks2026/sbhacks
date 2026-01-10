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

token = get_token()

class StravaApp:
    def __init__(self, token : str):
        self.token = token


def get_walking_activities(access_token):
    request_url = f'https://www.strava.com/api/v3/athlete/activities'
    header = {"Authorization" : "Bearer " + access_token}

    result = requests.get(request_url, headers=header).json()

    target_sports = {"Run", "Hike", "TrailRun"} # filter to only backpacking related things

    filtered_activities = [
        activity for activity in result
        if activity.get("sport_type") in target_sports
    ]
    
    return filtered_activities

print(get_walking_activities(token))