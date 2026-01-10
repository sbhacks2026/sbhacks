import sys
import json

# Get the access token passed from Node.js
access_token = sys.argv[1] if len(sys.argv) > 1 else "NO TOKEN RECEIVED"

# Return it as JSON
result = {
    "status": "success",
    "message": "Received access token!",
    "token": access_token,
    "token_length": len(access_token),
    "first_10_chars": access_token[:10] if access_token != "NO TOKEN RECEIVED" else "N/A"
}

print(json.dumps(result))