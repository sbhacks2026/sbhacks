from google import genai
import json


# Example we will input from Strava
recent_activities_json = "1. Mt. Whitney (11 miles), 2. Zion Narrows (5 miles)"
month_of_trip = "July"

# Reads strava_data.json file
# with open('strava_data.json', 'r', encoding='utf-8') as file:
#     recent_activities_json = json.load(file)

# month_of_trip = "Something Here"

# Prompt to submit to Gemini
prompt = f"""
I'm trying to plan a backpacking trip in {month_of_trip} and I'm looking for a trail. 
In order to tailor your search to my preferences, I will provide 
you with a list of my most recent activities along with some 
statistics for them in a json file. 

Here are my activities in order in the json: 
{recent_activities_json}

Based on my recent activities, return a suggested backpacking trail
showing me: 
    - the title at the top in bold
    - the distance in miles
    - elevation gain in feet 
    - a difficulty rating 
    - whether it's out & back or a loop
    - a quick summary of what to expect on the trail

Also search for a weather forecast in the area for {month_of_trip}, 
and if it's too early for a forecast, predict what the weather might 
look like in {month_of_trip} based on previous years.
"""

prompt = "Tell me a joke"

# Enter Gemini API key below
user_key = "AIzaSyDnFur1AGpaw-grKbouOiaiSU6FB_fTiy4"
client = genai.Client(api_key=user_key)

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt,
)

# Return ouptu
print(response.text)

