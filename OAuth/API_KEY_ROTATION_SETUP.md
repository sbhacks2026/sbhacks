# API Key Rotation Setup Guide

## Overview
The server now supports rotating through up to 4 different Strava API key sets to handle rate limits and increase the number of simultaneous authorizations.

## How It Works

1. **Round-Robin Rotation**: Each time a user clicks "Login with Strava", the server automatically rotates to the next API key set
2. **State Tracking**: The client ID is passed through the OAuth state parameter so the server knows which key was used
3. **Automatic Fallback**: If multiple key sets aren't configured, the system falls back to using a single key set

## Setting Up on Render

### Environment Variables to Add

Go to your Render dashboard → Your Web Service → Environment → Add the following variables:

#### API Key Set 1 (Required)
```
STRAVA_CLIENT_ID_1=your_first_client_id
STRAVA_CLIENT_SECRET_1=your_first_client_secret
```

#### API Key Set 2 (Optional)
```
STRAVA_CLIENT_ID_2=your_second_client_id
STRAVA_CLIENT_SECRET_2=your_second_client_secret
```

#### API Key Set 3 (Optional)
```
STRAVA_CLIENT_ID_3=your_third_client_id
STRAVA_CLIENT_SECRET_3=your_third_client_secret
```

#### API Key Set 4 (Optional)
```
STRAVA_CLIENT_ID_4=your_fourth_client_id
STRAVA_CLIENT_SECRET_4=your_fourth_client_secret
```

#### Other Required Variables
```
CALLBACK_URL=https://trailforge.onrender.com/callback
PORT=3000
```

## Creating Multiple Strava Apps

To get 4 different API key sets, you need to create 4 separate applications in Strava:

1. Go to https://www.strava.com/settings/api
2. Create a new application (you can name them "TrailForge 1", "TrailForge 2", etc.)
3. Set the **Authorization Callback Domain** to: `trailforge.onrender.com`
4. Copy the **Client ID** and **Client Secret** for each app
5. Add them to Render as environment variables using the format above

## Benefits

- **4x Capacity**: Instead of handling 1-2 simultaneous users, you can now handle 4-8 simultaneous users
- **Better Rate Limiting**: Distributes API calls across multiple apps
- **Automatic Rotation**: No manual intervention needed - the system automatically cycles through keys
- **Easy Scaling**: Add more keys by simply creating more Strava apps and adding environment variables

## Verification

When your server starts, you should see a log message like:
```
🔑 Loaded 4 API key set(s)
```

When users authenticate, you'll see:
```
🔄 Using API key set #1 (1/4 in rotation)
🔐 Exchanging token using API key set #1
```

## Backward Compatibility

If you don't set up numbered keys, the system will automatically fall back to using:
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`

This ensures your existing setup continues to work without any changes.
