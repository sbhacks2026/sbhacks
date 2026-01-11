const express = require('express');
const axios = require('axios');
const path = require('path');
const session = require('express-session');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// API Key Rotation System
class APIKeyRotator {
    constructor() {
        this.keys = [];
        this.currentIndex = 0;

        // Load all available API key sets from environment variables
        for (let i = 1; i <= 4; i++) {
            const clientId = process.env[`STRAVA_CLIENT_ID_${i}`];
            const clientSecret = process.env[`STRAVA_CLIENT_SECRET_${i}`];

            if (clientId && clientSecret) {
                this.keys.push({
                    clientId,
                    clientSecret,
                    index: i
                });
            }
        }

        // Fallback to original env vars if no numbered keys found
        if (this.keys.length === 0 && process.env.STRAVA_CLIENT_ID && process.env.STRAVA_CLIENT_SECRET) {
            this.keys.push({
                clientId: process.env.STRAVA_CLIENT_ID,
                clientSecret: process.env.STRAVA_CLIENT_SECRET,
                index: 0
            });
        }

        console.log(`🔑 Loaded ${this.keys.length} API key set(s)`);
    }

    getNextKey() {
        if (this.keys.length === 0) {
            throw new Error('No API keys configured');
        }

        const key = this.keys[this.currentIndex];
        this.currentIndex = (this.currentIndex + 1) % this.keys.length;

        console.log(`🔄 Using API key set #${key.index} (${this.currentIndex}/${this.keys.length} in rotation)`);
        return key;
    }
}

const apiKeyRotator = new APIKeyRotator();

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
    const currentKey = apiKeyRotator.getNextKey();
    res.json({
        clientId: currentKey.clientId,
        redirectUri: process.env.CALLBACK_URL || `http://localhost:${PORT}/callback`
    });
});

const { spawn } = require('child_process');

app.post('/auth/token', async (req, res) => {
    const { code, clientId } = req.body;

    if (!code) {
        return res.status(400).json({ error: 'Authorization code is required' });
    }

    try {
        // Find the matching API key set based on the clientId sent from frontend
        const keySet = apiKeyRotator.keys.find(k => k.clientId === clientId) || apiKeyRotator.keys[0];

        console.log(`🔐 Exchanging token using API key set #${keySet.index}`);

        // Exchange authorization code for access token
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: keySet.clientId,
            client_secret: keySet.clientSecret,
            code: code,
            grant_type: 'authorization_code'
        });

        const data = response.data;
        const accessToken = data.access_token;
        
        console.log('✅ User authenticated:', data.athlete.username);
        
        // CALL PYTHON SCRIPT to fetch activities
        let activities = [];
        try {
            console.log('🔵 Calling stravaApp.py to fetch activities...');
            
            const python = spawn('python3', [
                'stravaApp.py',
                accessToken  // Pass token to Python
            ]);

            let pythonOutput = '';
            let pythonError = '';

            python.stdout.on('data', (chunk) => {
                pythonOutput += chunk.toString();
            });

            python.stderr.on('data', (chunk) => {
                pythonError += chunk.toString();
            });

            // Wait for Python to finish
            await new Promise((resolve, reject) => {
                python.on('close', (code) => {
                    if (code !== 0) {
                        console.error('❌ Python error:', pythonError);
                        reject(new Error(pythonError));
                    } else {
                        resolve();
                    }
                });
            });

            // Parse the JSON returned by Python
            activities = JSON.parse(pythonOutput);
            console.log(`✅ Python fetched ${activities.length} activities`);
            
        } catch (fetchError) {
            console.error('⚠️ Error running Python script:', fetchError.message);
            // Continue anyway - we'll store empty array
        }
        
        // Store user data AND activities in session
        req.session.user = {
            athlete: data.athlete,
            activities: activities,
            expires_at: data.expires_at
        };

        // Save session before destroying it (to ensure data is persisted)
        await new Promise((resolve, reject) => {
            req.session.save((err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        // NOW deauthorize (we already have the data we need)
        try {
            const deauthResponse = await axios.post(`https://www.strava.com/oauth/deauthorize?access_token=${accessToken}`);
            console.log('✅ Deauthorized user - slot freed for next person!');
            console.log('✅ Deauth response:', deauthResponse.data);
            console.log('✅ Deauth status:', deauthResponse.status);
        } catch (deauthError) {
            console.error('⚠️ Error deauthorizing:', deauthError.message);
            console.error('⚠️ Full error:', deauthError.response?.data);
            console.error('⚠️ Status:', deauthError.response?.status);
            // Continue anyway
        }

        res.json({
            athlete: data.athlete,
            activities_count: activities.length,
            message: 'Successfully authenticated and fetched activities'
        });

    } catch (error) {
        console.error('❌ Error exchanging token:', error.response?.data || error.message);
        
        // Check if it's the "too many athletes" error
        if (error.response?.data?.message?.toLowerCase().includes('athlete')) {
            return res.status(429).json({ 
                error: 'Too many athletes connected. Please try again in a moment.',
                details: error.response?.data 
            });
        }
        
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
        // Use the same key rotation for refresh tokens
        const keySet = apiKeyRotator.getNextKey();

        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: keySet.clientId,
            client_secret: keySet.clientSecret,
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

// Get athlete's activities - USES STORED DATA (no Strava API call needed!)
app.get('/api/activities', async (req, res) => {
    // Check if this user has a session with activities
    if (!req.session.user || !req.session.user.activities) {
        return res.status(401).json({ error: 'Not authenticated. Please log in first.' });
    }

    try {
        // Pass stored activities to Python (as JSON string)
        const activitiesJson = JSON.stringify(req.session.user.activities);
        
        const python = spawn('python3', [
            'stravaApp.py',
            activitiesJson  // Pass activities data, not a token
        ]);

        let result = '';
        let errorOutput = '';

        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('❌ Python error:', errorOutput);
                return res.status(500).json({ 
                    error: 'Failed to analyze activities',
                    details: errorOutput 
                });
            }

            try {
                const analysis = JSON.parse(result);
                res.json(analysis);
            } catch (parseError) {
                console.error('❌ Failed to parse Python output:', result);
                res.status(500).json({ 
                    error: 'Failed to parse analysis results',
                    details: parseError.message,
                    raw_output: result
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
            await axios.post(`https://www.strava.com/oauth/deauthorize?access_token=${req.session.user.access_token}`);
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

// Get trail recommendation from Gemini
app.get('/api/recommendation', async (req, res) => {
    // Check if this user has a session with activities
    if (!req.session.user || !req.session.user.activities) {
        return res.status(401).json({ error: 'Not authenticated. Please log in first.' });
    }


    try {
        // Get user preferences (with defaults)
        const preferences = req.session.user.preferences || {
            month: 'July',
            city: 'Santa Barbara, CA',
            drivingHours: '2',
            difficulty: 'Moderate',
            drivingHours: '2',
            difficulty: 'Moderate',
            desiredLocation: ''
        };

        // Pass stored activities to Python gemini_prompt.py (as JSON string)
        const activitiesJson = JSON.stringify(req.session.user.activities);

        console.log(`Passing ${req.session.user.activities.length} activities to gemini_prompt.py`);
        console.log('User preferences:', preferences);

        const python = spawn('python3', [
            '../gemini_prompt.py',  // Path relative to OAuth folder
            activitiesJson,  // Pass activities data
            preferences.month,
            preferences.city,
            preferences.drivingHours,
            preferences.difficulty,
            preferences.drivingHours,
            preferences.difficulty,
            preferences.desiredLocation || ''
        ]);

        let result = '';
        let errorOutput = '';

        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('❌ Python error:', errorOutput);
                return res.status(500).json({
                    error: 'Failed to generate recommendation',
                    details: errorOutput
                });
            }

            // Return the recommendation text
            res.json({ recommendation: result.trim() });
        });

    } catch (error) {
        console.error('Error running gemini_prompt.py:', error.message);
        res.status(500).json({
            error: 'Failed to generate recommendation',
            details: error.message
        });
    }
});

// Raw Gemini output endpoint (for testing)
app.get('/api/raw-recommendation', async (req, res) => {
    // Check if this user has a session with activities
    if (!req.session.user || !req.session.user.activities) {
        return res.status(401).send('Not authenticated. Please log in first.');
    }

    try {
        // Pass stored activities to Python gemini_prompt.py (as JSON string)
        const activitiesJson = JSON.stringify(req.session.user.activities);

        const python = spawn('python3', [
            '../gemini_prompt.py',
            activitiesJson
        ]);

        let result = '';
        let errorOutput = '';

        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('❌ Python error:', errorOutput);
                return res.status(500).send(`Error: ${errorOutput}`);
            }

            // Return raw text output
            res.setHeader('Content-Type', 'text/plain');
            res.send(result);
        });

    } catch (error) {
        console.error('Error running gemini_prompt.py:', error.message);
        res.status(500).send(`Error: ${error.message}`);
    }
});

// Save user preferences
app.post('/api/preferences', (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { month, city, drivingHours, difficulty, desiredLocation } = req.body;

    // Store preferences in session
    req.session.user.preferences = {
        month: month || 'July',
        city: city || 'Santa Barbara, CA',
        drivingHours: drivingHours || '2',
        difficulty: difficulty || 'Moderate',
        drivingHours: drivingHours || '2',
        difficulty: difficulty || 'Moderate',
        desiredLocation: desiredLocation || ''
    };

    console.log('Saved user preferences:', req.session.user.preferences);

    res.json({ success: true });
});

// Serve preferences page
app.get('/preferences', (req, res) => {
    res.sendFile(path.join(__dirname, 'preferences.html'));
});

// Serve results page
app.get('/results', (req, res) => {
    res.sendFile(path.join(__dirname, 'results.html'));
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

