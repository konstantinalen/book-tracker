const mysql = require('mysql2/promise');
require('dotenv').config(); // populate .env's variables with info

const dbConfig = {
    host: process.env.DB_HOST, // || 'localhost',
    user: process.env.DB_USER, // || 'root',
    password: process.env.DB_PASSWORD // || 'your_password' 
};

const DB_NAME = process.env.DB_NAME || 'library_tracker';

let pool;

async function initializeDatabase() {
    console.log("Checking database schema...");
    
    // 1. Connect without a specific database
    const connection = await mysql.createConnection(dbConfig);
    
    // 2. Create the Database if it's missing
    await connection.query(`CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;`);
    await connection.query(`USE \`${DB_NAME}\`;`);

    // 3. Create the Books Table
    await connection.query(`
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            epc VARCHAR(50) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255),
            status ENUM('IN', 'OUT', 'UNKNOWN') DEFAULT 'UNKNOWN',
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `);

    // 4. Create the Scan Logs Table
    await connection.query(`
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            epc VARCHAR(50) NOT NULL,
            reader_ip VARCHAR(50),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `);

    // 5. Create the "Tripwire" Trigger for automatic last_seen updates
    await connection.query(`DROP TRIGGER IF EXISTS update_book_last_seen;`);
    await connection.query(`
        CREATE TRIGGER update_book_last_seen
        AFTER INSERT ON scan_logs
        FOR EACH ROW
        BEGIN
            UPDATE books 
            SET last_seen = NEW.timestamp 
            WHERE epc = NEW.epc;
        END;
    `);

    console.log("✅ Database schema and triggers are armed and ready.");
    await connection.end();

    // 6. Now that it exists, create the persistent Pool for the app to use
    pool = mysql.createPool({
        ...dbConfig,
        database: DB_NAME,
        waitForConnections: true,
        connectionLimit: 10,
        queueLimit: 0
    });

    return pool;
}

module.exports = {
    initializeDatabase,
    getPool: () => pool 
};