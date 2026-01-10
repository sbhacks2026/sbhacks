import json
import requests

def get_keys(path='config.json'):
    try:
        with open(path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file {path} not found.")
        return None

config = get_keys()
id = config.get('CLIENT_ID')
secret = config.get('CLIENT_SECRET')
referesh_token = config.get('CODE')

def get_token():
    auth_url = "https://www.strava.com/oauth/token"
    data = {
        'client_id' : id,
        'client_secret' : secret,
        'grant_type' : 'refresh_token',
        'refresh_token' : referesh_token
    }

    #request
    auth_result = requests.post(auth_url, data=data).json()
    access_token = auth_result['access_token']
    return access_token

def get_segment_stats(id, access_token):
    request_url = f'https://www.strava.com/api/v3/segments/{id}'
    header = {"Authorization" : "Bearer " + access_token}

    result = requests.get(request_url, headers=header).json()
    
    try:
        return [result['effort_count'], result['athlete_count']]
    except:
        print('Error with id:', id)
        return [0, 0]