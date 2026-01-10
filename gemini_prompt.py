from google import genai
import json

# Enter Gemini API key below
with open('key.json', 'r', encoding='utf-8') as key_file:
    key_dict = json.load(key_file)
    user_key = key_dict['user_key']

# Example we will input from Strava
month_of_trip = "July" # change to user input
# recent_activities_json = "1. Mt. Whitney (11 miles), 2. Zion Narrows (5 miles)"

# Reads strava_data.json file
with open('strava_data.json', 'r', encoding='utf-8') as file:
    recent_activities_json = json.load(file)

# Prompt to submit to Gemini
prompt = f"""
I'm trying to plan a backpacking trip in {month_of_trip} and I'm looking for a trail. 
In order to tailor your search to my preferences, I will provide 
you with a list of my most recent activities along with some 
statistics for them in a json file. 

Here are my activities in order in the json: 
{recent_activities_json}
    Note: 
        - Mostly ignore the name of the activities and the id
        - Record the general location of the lat/lng coordinates
        to understand where the user might be currently located
        based off of repeating locations so you can suggest
        nearby backpacking trail, as well as one that is in a 
        new unexplored area

Based on my recent activities, return a suggested backpacking trail
showing me: 
    - the title at the top in bold
    - the distance in miles
    - elevation gain in feet 
    - a difficulty rating 
    - whether it's out & back or a loop
    - a quick summary of what to expect on the trail

When returning the suggested trail, tell me how many days/nights
you think it will take. 

Also, search for a weather forecast in the area for {month_of_trip}, 
and if it's too early for a forecast, predict what the weather might 
look like in {month_of_trip} based on previous years. Return this 
in a very brief statement of what conditions to expect.
"""

client = genai.Client(api_key=user_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Return ouptut
print(response.text)

