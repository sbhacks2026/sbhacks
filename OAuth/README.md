# Strava OAuth Authentication Setup

## Overview
This is a simple implementation of Strava OAuth 2.0 authentication that allows users to log in with their Strava account.

## OAuth Flow
1. User clicks "Login with Strava" button on your website
2. User is redirected to Strava's authorization page
3. User approves the connection
4. Strava redirects back to your callback URL with an authorization code
5. Your server exchanges the code for an access token
6. You can now make API requests on behalf of the user

## Setup Steps

### 1. Get Your Strava API Credentials
- Go to https://www.strava.com/settings/api
- Note your **Client ID** and **Client Secret**
- Set your **Authorization Callback Domain** (e.g., `localhost` for local development or your domain)

### 2. Environment Variables
Create a `.env` file in the root directory with:
```
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
CALLBACK_URL=http://localhost:3000/callback
```

### 3. File Structure
```
project/
├── index.html          # Landing page with login button
├── callback.html       # Page that handles the OAuth callback
├── server.js           # Node.js backend server
├── package.json        # Dependencies
├── .env                # Environment variables (don't commit!)
└── README.md           # This file
```

### 4. Install Dependencies
```bash
npm install
```

### 5. Run the Server
```bash
npm start
```

### 6. Test
Navigate to http://localhost:3000 and click "Login with Strava"

## Important Notes
- Never expose your Client Secret in client-side code
- The token exchange must happen on your backend server
- Store access tokens securely (not in localStorage for production apps)
