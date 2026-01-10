# import packages
from google import genai

user_key = "AIzaSyDnFur1AGpaw-grKbouOiaiSU6FB_fTiy4"
client = genai.Client(api_key = user_key)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words",
)

print(response.text)
