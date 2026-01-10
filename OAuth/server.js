const express = require('express');
const axios = require('axios');
const path = require('path');
const session = require('express-session');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(__dirname));

// Session middleware - stores each user's data separately
app.use(session({
    secret: 'your-secret-key-change-this-in-production', // Change this!
    resave: false,
    saveUninitialized: false,
    cookie: { 
        secure: false, // Set to true if using HTTPS in production
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));

// Configuration endpoint
app.get('/auth/config', (req, res) => {
    res.json({
        clientId: process.env.STRAVA_CLIENT_ID,
        redirectUri: process.env.CALLBACK_URL || `http://localhost:${PORT}/callback`
    });
});

// Token exchange endpoint - NOW STORES PER USER
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
        
        // Store THIS user's data in THEIR session
        req.session.user = {
            athlete: data.athlete,
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            expires_at: data.expires_at
        };
        
        console.log('User authenticated:', data.athlete.username, '- Session ID:', req.sessionID);
        
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

// Refresh token endpoint
app.post('/auth/refresh', async (req, res) => {
    if (!req.session.user || !req.session.user.refresh_token) {
        return res.status(401).json({ error: 'No user session found' });
    }

    try {
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: process.env.STRAVA_CLIENT_ID,
            client_secret: process.env.STRAVA_CLIENT_SECRET,
            refresh_token: req.session.user.refresh_token,
            grant_type: 'refresh_token'
        });

        const data = response.data;
        
        // Update this user's session with new tokens
        req.session.user.access_token = data.access_token;
        req.session.user.refresh_token = data.refresh_token;
        req.session.user.expires_at = data.expires_at;
        
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

// Get athlete's activities - USES EACH USER'S OWN TOKEN
app.get('/api/activities', async (req, res) => {
    // Check if this user has a session with a token
    if (!req.session.user || !req.session.user.access_token) {
        return res.status(401).json({ error: 'Not authenticated. Please log in first.' });
    }

    try {
        // Use THIS user's token from THEIR session
        const response = await axios.get('https://www.strava.com/api/v3/athlete/activities', {
            headers: {
                'Authorization': `Bearer ${req.session.user.access_token}`
            },
            params: {
                per_page: 10
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

// Get current user info
app.get('/api/me', (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    res.json({
        athlete: req.session.user.athlete,
        sessionId: req.sessionID
    });
});

// Logout endpoint
app.post('/auth/logout', async (req, res) => {
    if (req.session.user && req.session.user.access_token) {
        try {
            // Deauthorize with Strava
            await axios.post('https://www.strava.com/oauth/deauthorize', null, {
                headers: {
                    'Authorization': `Bearer ${req.session.user.access_token}`
                }
            });
        } catch (error) {
            console.log('Error deauthorizing:', error.message);
        }
    }
    
    // Destroy this user's session
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to logout' });
        }
        res.json({ success: true, message: 'Logged out successfully' });
    });
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
    console.log(`Make sure to set your Strava callback URL to: ${process.env.CALLBACK_URL || `http://localhost:${PORT}/callback`}`);
});
