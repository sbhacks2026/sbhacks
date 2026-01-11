# sbhacks
# About the project

## Inspiration
As outdoor enthusiasts, we were all interested in getting into backpacking, but we didn't know where to start to find trails perfect for our skill level and know-how. We'd all hiked before and are active, valuing our physical and mental health, so had Strava accounts with records of past hikes, runs, and walks. With access to this data, we created a trail recommender based on a user's experience, using statistics from their Strava activities.

## What it does
So, insteaed of asking users to guess their fitness level, we extract it from Strava with Strava's API and Google Gemini. Data from Strava's log of past activity is processed into a JSON alongside user inputted preferences like hike location/distance away from current location and relative hike difficulty. Gemini then analyzes the user's capabilities and preferences against potential trails to recommend a tailored route that is both safe and challenging. Our website provides a summary of the user's past activity along with a description of the recommended trail complete with statistics, permit information (if applicable), and an embedded AllTrails map.
