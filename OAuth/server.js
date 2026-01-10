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

// Token exchange endpoint - GET TOKEN THEN KICK USER OUT
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
        
        // IMMEDIATELY deauthorize from Strava (frees up the slot!)
        try {
            await axios.post('https://www.strava.com/oauth/deauthorize', null, {
                headers: {
                    'Authorization': `Bearer ${data.access_token}`
                }
            });
            console.log('User deauthorized from Strava (freed up slot for next user)');
        } catch (deauthError) {
            console.log('Error deauthorizing:', deauthError.message);
        }
        
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

const { spawn } = require('child_process');

// Get athlete's activities - RUNS PYTHON THEN DEAUTHORIZES
app.get('/api/activities', async (req, res) => {
    // Check if this user has a session with a token
    if (!req.session.user || !req.session.user.access_token) {
        return res.status(401).json({ error: 'Not authenticated. Please log in first.' });
    }

    const accessToken = req.session.user.access_token;

    try {
        // Call Python script with user's access token
        const python = spawn('python3', [
            'testpy.py',
            accessToken
        ]);

        let result = '';
        let errorOutput = '';

        // Collect data from Python script
        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        // When Python finishes
        python.on('close', async (code) => {
            // DEAUTHORIZE NOW (after Python got the data)
            try {
                await axios.post('https://www.strava.com/oauth/deauthorize', null, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                console.log('Deauthorized user after fetching activities');
            } catch (deauthError) {
                console.log('Error deauthorizing:', deauthError.message);
            }

            if (code !== 0) {
                console.error('Python error:', errorOutput);
                return res.status(500).json({ 
                    error: 'Failed to analyze activities',
                    details: errorOutput 
                });
            }

            try {
                // Parse and return Python's JSON output
                const analysis = JSON.parse(result);
                res.json(analysis);
            } catch (parseError) {
                console.error('Failed to parse Python output:', result);
                res.status(500).json({ 
                    error: 'Failed to parse analysis results',
                    details: parseError.message 
                });
            }
        });

    } catch (error) {
        console.error('Error running Python script:', error.message);
        res.status(500).json({ 
            error: 'Failed to run analysis',
            details: error.message 
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

