from google import genai
import os
import sys

user_key = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=user_key)

if len(sys.argv) > 1:
    trail_name = sys.argv[1]
    # Prompt Gemini to find the specific URL
    prompt = f"Find the official AllTrails URL for the trail named '{trail_name}'. Return ONLY the URL, nothing else."

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    print(response.text.strip())