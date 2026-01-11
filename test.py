from google import genai

prompt = f"""
I'm trying to plan a backpacking trip in July and I'm looking for a trail. 


Return a suggested backpacking trail
showing me: 
    - the title at the top in bold
    - the distance in miles
    - elevation gain in feet 
    - a difficulty rating 
    - whether it's out & back or a loop
    - a quick summary of what to expect on the trail

Also search for a weather forecast in the area for July, 
and if it's too early for a forecast, predict what the weather might 
look like in July based on previous years.
"""

user_key = "AIzaSyDnFur1AGpaw-grKbouOiaiSU6FB_fTiy4"
client = genai.Client(api_key=user_key)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
)

print(response.text)