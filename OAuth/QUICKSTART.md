# Quick Start Guide - Strava OAuth

## For Team Members

This guide will help you get the Strava OAuth authentication running on your local machine.

## Prerequisites
- Node.js installed (v14 or higher)
- A Strava account
- Strava API credentials (Client ID and Client Secret)

## Step-by-Step Setup

### 1. Get Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. If you don't have an app, create one:
   - **Application Name**: Your app name
   - **Category**: Choose appropriate category
   - **Club**: Leave blank
   - **Website**: http://localhost:3000 (for local dev)
   - **Authorization Callback Domain**: localhost
3. Note down your **Client ID** and **Client Secret**

### 2. Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   STRAVA_CLIENT_ID=12345
   STRAVA_CLIENT_SECRET=abcdef123456789
   CALLBACK_URL=http://localhost:3000/callback
   PORT=3000
   ```

### 3. Install Dependencies

```bash
npm install
```

### 4. Run the Server

```bash
npm start
```

You should see:
```
Server running on http://localhost:3000
Make sure to set your Strava callback URL to: http://localhost:3000/callback
```

### 5. Test the OAuth Flow

1. Open your browser to http://localhost:3000
2. Click "Login with Strava"
3. You'll be redirected to Strava to authorize
4. After authorizing, you'll be redirected back with your athlete info

## How It Works

### OAuth Flow Diagram
```
User                    Your App                Strava
  |                        |                       |
  |  Click "Login"         |                       |
  |----------------------->|                       |
  |                        |                       |
  |  Redirect to Strava    |                       |
  |------------------------------------------------>|
  |                        |                       |
  |  User approves         |                       |
  |                        |                       |
  |  Redirect with code    |                       |
  |<------------------------------------------------|
  |                        |                       |
  |  Send code to server   |                       |
  |----------------------->|                       |
  |                        |  Exchange code        |
  |                        |  for token            |
  |                        |---------------------->|
  |                        |                       |
  |                        |  Return access token  |
  |                        |<----------------------|
  |  Display success       |                       |
  |<-----------------------|                       |
```

## File Structure Explained

```
project/
├── index.html          # Landing page with "Login with Strava" button
├── callback.html       # Handles the redirect from Strava
├── server.js           # Node.js backend that exchanges codes for tokens
├── package.json        # Node dependencies
├── .env                # Your API credentials (KEEP SECRET!)
├── .env.example        # Template for .env file
└── README.md           # Full documentation
```

## Common Issues

### "Invalid redirect_uri"
- Make sure your callback URL in `.env` matches exactly what's in Strava API settings
- For local development, use `http://localhost:3000/callback`

### "Invalid client"
- Double-check your Client ID and Client Secret in `.env`
- Make sure there are no extra spaces

### Port already in use
- Change the PORT in `.env` to something else (e.g., 3001)
- Update your Strava callback URL accordingly

## Next Steps for Your Team

As the team member responsible for authorization:

1. **Share this code** with your team via Git (but NOT the .env file!)
2. **Document the scopes** you need (currently set to `read,activity:read_all`)
3. **Plan token storage**: In production, you'll need to:
   - Store tokens in a database
   - Create user sessions
   - Handle token refresh automatically

## Available Scopes

Common Strava scopes you might need:
- `read` - Read public data
- `read_all` - Read private activities
- `activity:read` - Read activity data
- `activity:read_all` - Read all activity data
- `activity:write` - Create and update activities

Edit the scope in `index.html` line 63:
```javascript
const scope = 'read,activity:read_all'; // Adjust as needed
```

## Questions?

Check out:
- Strava API Docs: https://developers.strava.com/docs/
- OAuth 2.0 Guide: https://oauth.net/2/
