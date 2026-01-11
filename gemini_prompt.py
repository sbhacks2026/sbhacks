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
You are an expert outdoor guide and trip planner.

I am planning a backpacking trip in {month_of_trip}. 
To tailor the recommendation to my capabilities, please analyze my recent activity history provided below.

<activity_history>
{json.dumps(recent_activities_json, indent=2)}
</activity_history>

Analysis Instructions:
1. **Location**: Identify my general "home base" from the coordinates to suggest nearby trails vs. destination trails.
2. **Fitness Level**: 
   - Prioritize 'Hike' activities to judge my comfort with distance and elevation gain.
   - Use 'Run' and other activities as secondary indicators of general cardio fitness.
   - Ignore specific activity names or IDs.

Based on this analysis, please recommend **two** distinct backpacking options:
1. **The Local Option**: A great trail within a few hours of my calculated location.
2. **The Destination Option**: A highly-rated trail in a new, exciting area suitable for {month_of_trip}.

For EACH option, provide the following details in Markdown:
*   **Trail Name** (Bold)
*   **Location** (Region/State)
*   **Distance & Elevation**: Total miles and feet of gain.
*   **Difficulty Rating**: Explain *why* it fits my fitness level (e.g., "Challenging but doable based on your recent 11-mile hike...").
*   **Route Type**: (Loop / Out & Back).
*   **Itinerary**: Suggested Days/Nights.
*   **Summary**: What to expect (scenery, terrain).
*   **Weather**: Expected conditions for {month_of_trip} (historical averages).
*   **Link**: AllTrails website link.
"""

client = genai.Client(api_key=user_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Return ouptut
print(response.text)
