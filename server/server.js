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

app.get('/api/allbooks', async (req, res) => {
    try {
        const pool = dbModule.getPool();
        const [rows] = await pool.query('SELECT * FROM books');
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/scans', async (req, res) => {
    try {
        const pool = dbModule.getPool();
        const [rows] = await pool.query(`
            SELECT 
                l.id, 
                b.title, 
                b.author, 
                b.status, 
                l.timestamp as last_seen 
            FROM scan_logs l
            JOIN books b ON l.epc = b.epc
            ORDER BY l.timestamp DESC 
        `);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

async function startApp() {
    try {
        // 1. Build the database if it doesn't exist
        await dbModule.initializeDatabase();
        
        // 2. Once DB is ready, start the web server
        server.listen(3000, () => {
            console.log('🚀 Backend running on http://localhost:3000');
            console.log('📡 Waiting for hardware...');
        });
        
    } catch (error) {
        console.error("❌ CRITICAL FAILURE: Could not start app.", error);
        process.exit(1);
    }
}

startApp();
