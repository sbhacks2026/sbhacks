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

# Accept arguments from Node.js server
if len(sys.argv) > 1:
    # Activities passed as JSON string from server.js
    recent_activities_json = json.loads(sys.argv[1])

    # User preferences (with defaults if not provided)
    month_of_trip = sys.argv[2] if len(sys.argv) > 2 else "July"
    current_location = sys.argv[3] if len(sys.argv) > 3 else "Santa Barbara, CA"
    driving_hours = sys.argv[4] if len(sys.argv) > 4 else "2"
    difficulty = sys.argv[5] if len(sys.argv) > 5 else "Moderate"
    desired_location = sys.argv[6] if len(sys.argv) > 6 else ""
else:
    # Fallback: Reads strava_data.json file for local testing
    with open('strava_data.json', 'r', encoding='utf-8') as file:
        recent_activities_json = json.load(file)

    # Default values for local testing
    month_of_trip = "July"
    current_location = "Santa Barbara, CA"
    driving_hours = "2"
    difficulty = "Moderate"
    desired_location = ""

# Prompt to submit to Gemini
prompt = f"""
I'm planning a backpacking trip in {month_of_trip} and need help finding the right trail.

## My Location and Constraints

- **Current Location**: {current_location}
- **Willing to Drive**: Up to {driving_hours} hours
- **Desired predicted difficulty based on my skills**: {difficulty}
- **Trip Month**: {month_of_trip}

## My Activity Data

I've provided my recent outdoor activities as JSON data below. Use this to understand my preferences and fitness level:

{recent_activities_json}

## How to Analyze My Activities

When reviewing my activity data:
- **Activity types**: Prioritize hiking activities as the strongest indicator of trail preferences (terrain, difficulty, distance). Use runs and other activities as secondary indicators of general fitness and endurance.
- **Distance & elevation**: Look at my typical distances and elevation gains to gauge appropriate trail difficulty.

## Trail Recommendation Format

Please recommend ONE backpacking trail that matches my {difficulty} difficulty preference adjusted for my ability as seen in the activity data, and is within {driving_hours} hours driving distance from {current_location}.
In addition, if there is a valid location submitted here: {desired_location}, (not just blank space between the colon and the comma) find hikes in that area within {driving_hours} hours driving distance from {desired_location} instead of {current_location}.

Format your response as follows:

**[Trail Name]**
- **Distance**: X miles
- **Elevation Gain**: X feet
- **Difficulty**: [Easy/Moderate/Strenuous]
- **Trail Type**: [Loop/Out & Back/Point-to-Point]
- **Recommended Duration**: X days / X nights
- **Permit Required**: [Yes/No] (In a separate paragraph)

**Trail Summary**: [2-3 sentences describing terrain, scenery, highlights, and what to expect. If a permit is required, briefly explain how to obtain it and any lottery/reservation system details]

**Weather Forecast for {month_of_trip}**: [Brief statement about expected conditions. If a specific forecast isn't available, provide typical weather patterns for this location and month based on historical data]

**AllTrails Link**: [URL to the trail page]

## Additional Notes
- Focus the recommendation on a single, well-matched trail rather than multiple options
- Consider seasonal factors (snow, heat, water availability) when suggesting timing
- If my activity history suggests I'm not ready for multi-day backpacking, recommend a challenging day hike or easy one night instead and explain why
"""

client = genai.Client(api_key = user_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Return ouptut
print(response.text)
