const express = require('express');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(__dirname)); // Serve static files

// Configuration endpoint (provides client ID to frontend)
app.get('/auth/config', (req, res) => {
    res.json({
        clientId: process.env.STRAVA_CLIENT_ID,
        redirectUri: process.env.CALLBACK_URL || `http://localhost:${PORT}/callback`
    });
});

// Token exchange endpoint
app.post('/auth/token', async (req, res) => {
    const { code } = req.body;

    if (!code) {
        return res.status(400).json({ error: 'Authorization code is required' });
    }

    try {
        // Exchange authorization code for access token
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: process.env.STRAVA_CLIENT_ID,
            client_secret: process.env.STRAVA_CLIENT_SECRET,
            code: code,
            grant_type: 'authorization_code'
        });

        const data = response.data;
        
        // In a real application, you would:
        // 1. Store the access_token and refresh_token in a secure database
        // 2. Create a session for the user
        // 3. Return a session token to the frontend
        
        // For demonstration purposes, we're returning the full response
        console.log('Successfully authenticated user:', data.athlete.username);
        
        res.json({
            athlete: data.athlete,
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            expires_at: data.expires_at,
            expires_in: data.expires_in
        });

    } catch (error) {
        console.error('Error exchanging token:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to exchange authorization code',
            details: error.response?.data || error.message 
        });
    }
});

// Refresh token endpoint (for when access token expires)
app.post('/auth/refresh', async (req, res) => {
    const { refresh_token } = req.body;

    if (!refresh_token) {
        return res.status(400).json({ error: 'Refresh token is required' });
    }

    try {
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: process.env.STRAVA_CLIENT_ID,
            client_secret: process.env.STRAVA_CLIENT_SECRET,
            refresh_token: refresh_token,
            grant_type: 'refresh_token'
        });

        const data = response.data;
        
        res.json({
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            expires_at: data.expires_at,
            expires_in: data.expires_in
        });

    } catch (error) {
        console.error('Error refreshing token:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to refresh token',
            details: error.response?.data || error.message 
        });
    }
});

// Example API endpoint - Get athlete's activities
app.get('/api/activities', async (req, res) => {
    const accessToken = req.headers.authorization?.replace('Bearer ', '');

    if (!accessToken) {
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        const response = await axios.get('https://www.strava.com/api/v3/athlete/activities', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            params: {
                per_page: 10 // Get 10 most recent activities
            }
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error fetching activities:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to fetch activities',
            details: error.response?.data || error.message 
        });
    }
});

// Serve callback page
app.get('/callback', (req, res) => {
    res.sendFile(path.join(__dirname, 'callback.html'));
});

// Serve index page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Make sure to set your Strava callback URL to: http://localhost:${PORT}/callback`);
});
