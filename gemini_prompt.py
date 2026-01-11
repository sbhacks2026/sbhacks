from google import genai
import json
import os
import sys


# Uncomment below when pushing for website demo
user_key = os.environ.get('GEMINI_API_KEY')


# # Enter Gemini API key below
# with open('key.json', 'r', encoding='utf-8') as key_file:
#     key_dict = json.load(key_file)
#     user_key = key_dict['user_key']

# Example we will input from Strava
month_of_trip = "July" # change to user input
current_location = "Santa Barbara, CA"

# Accept activities as command-line argument from Node.js
if len(sys.argv) > 1:
    # Activities passed as JSON string from server.js
    recent_activities_json = json.loads(sys.argv[1])
else:
    # Fallback: Reads strava_data.json file for local testing
    with open('strava_data.json', 'r', encoding='utf-8') as file:
        recent_activities_json = json.load(file)

# Prompt to submit to Gemini
prompt = f"""
I'm planning a backpacking trip in {month_of_trip} and need help finding the right trail.

## My Activity Data

I've provided my recent outdoor activities as JSON data below. Use this to understand my preferences and fitness level:

{recent_activities_json}

## How to Analyze My Activities

When reviewing my activity data:
- **Activity types**: Prioritize hiking activities as the strongest indicator of trail preferences (terrain, difficulty, distance). Use runs and other activities as secondary indicators of general fitness and endurance.
- **Distance & elevation**: Look at my typical distances and elevation gains to gauge appropriate trail difficulty.

## Trail Recommendation Format

Please recommend ONE backpacking trail and format your response as follows:

**[Trail Name]**
- **Distance**: X miles
- **Elevation Gain**: X feet  
- **Difficulty**: [Easy/Moderate/Strenuous]
- **Trail Type**: [Loop/Out & Back/Point-to-Point]
- **Recommended Duration**: X days / X nights

**Trail Summary**: [2-3 sentences describing terrain, scenery, highlights, and what to expect]

**Weather Forecast for {month_of_trip}**: [Brief statement about expected conditions. If a specific forecast isn't available, provide typical weather patterns for this location and month based on historical data]

**AllTrails Link**: [URL to the trail page]

## Additional Notes
- Focus the recommendation on a single, well-matched trail rather than multiple options
- Consider seasonal factors (snow, heat, water availability) when suggesting timing
- If my activity history suggests I'm not ready for multi-day backpacking, recommend a challenging day hike instead and explain why
"""

client = genai.Client(api_key = user_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Return ouptut
print(response.text)
