const express = require('express');
const { spawn } = require('child_process');
const http = require('http');
const { Server } = require("socket.io");
const cors = require('cors');
const dbModule = require('./database'); 

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

// --- API ENDPOINTS ---

// Fetch all known books
app.get('/api/books', async (req, res) => {
    try {
        // 1. Call getPool(), and destructure [rows] from mysql2
        const [rows] = await dbModule.getPool().query("SELECT * FROM books ORDER BY last_seen DESC");
        res.json(rows);
    } catch (err) {
        console.error(err);
        // 2. Always send JSON back so Vue doesn't crash on text!
        res.status(500).json({ error: "Database error" }); 
    }
});

// Fetch the 50 most recent scan events
app.get('/api/events', async (req, res) => {
    try {
        const query = `
            SELECT scan_logs.id, scan_logs.epc, scan_logs.reader_name, scan_logs.timestamp, books.title 
            FROM scan_logs 
            LEFT JOIN books ON scan_logs.epc = books.epc 
            ORDER BY scan_logs.timestamp DESC LIMIT 50
        `;
        const [rows] = await dbModule.getPool().query(query);
        res.json(rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Database error" });
    }
});
// --- END API ENDPOINTS ---

async function startApp() {
    try {
        // 1. Build the database if it doesn't exist
        await dbModule.initializeDatabase();
        
        // 2. Once DB is ready, start the web server
        server.listen(3000, () => {
            console.log('🚀 Backend running on http://localhost:3000');
            console.log('📡 Starting hardware tracker...');
            
            // 3. Boot up the Python hardware script!
            // Note: If 'python' doesn't work on your Windows machine, 
            // you may need to change it to 'python3' or your full path to python.exe
            const tracker = spawn('python', ['-u', 'tracker.py']); 

            // Listen for normal Python print() statements
            // Listen for normal Python print() statements
            tracker.stdout.on('data', (data) => {
                const output = data.toString().trim();
                console.log(`🐍 [TRACKER]: ${output}`);
                
                // If Python says it just updated the DB, broadcast a WebSocket event!
                if (output.includes("Database Updated Successfully")) {
                    io.emit('new_scan_event');
                }
            });
            // Listen for Python crashes or errors
            tracker.stderr.on('data', (data) => {
                console.error(`🚨 [TRACKER ERROR]: ${data.toString().trim()}`);
            });

            // Listen for the script closing/crashing
            tracker.on('close', (code) => {
                console.log(`⚠️ [TRACKER] Process exited with code ${code}`);
            });
        });
        
    } catch (error) {
        console.error("❌ CRITICAL FAILURE: Could not start app.", error);
        process.exit(1);
    }
}

startApp();
