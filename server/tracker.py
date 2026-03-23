import hid
import time
import pymysql
import os
from dotenv import load_dotenv

# Load the variables from your .env file into Python's environment
load_dotenv()

# Hardware Info
VID = 0x04D8
PID = 0x033F
READER_NAME = "Desk_USB_Scanner"

# Database Connection using Environment Variables
try:
    db = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor()
    print(">>> Database connection established securely.")
except Exception as e:
    print(f">>> FAILED TO CONNECT TO DATABASE: {e}")
    exit()


def log_tag(epc_string):
    print(f"\n>>> PROCESSING TAG: {epc_string}")
    
    try:
        # 1. Log the raw scan event
        cursor.execute(
            "INSERT INTO scan_logs (epc, reader_name) VALUES (%s, %s)", 
            (epc_string, READER_NAME)
        )
        
        # 2. Upsert the book inventory
        upsert_query = """
            INSERT INTO books (epc, status, last_seen) 
            VALUES (%s, 'IN', NOW()) 
            ON DUPLICATE KEY UPDATE last_seen = NOW(), status = 'IN';
        """
        cursor.execute(upsert_query, (epc_string,))
        
        db.commit()
        print(">>> Database Updated Successfully.")
        
    except Exception as e:
        print(f">>> DB ERROR: {e}")

print("--- LIBRARY INVENTORY TRACKER ONLINE ---")

try:
    device = hid.device()
    device.open(VID, PID)
    device.set_nonblocking(1) # Read instantly, don't wait
    print(f">>> Connected to scanner: {READER_NAME}")
    print(">>> Listening for tags...\n")
    
    # We use a set to track tags we just saw, to prevent blasting the DB 20 times a second
    recent_tags = {}
    
    while True:
        # 1. Grab data from the USB pipe
        response = device.read(64)
        
        if response:
            hex_str = bytes(response).hex().upper()
            
            # 2. Look for the "Auto Send to SU" packet (CC FF FF 20 05)
            if "CCFFFF2005" in hex_str:
                idx = hex_str.find("CCFFFF2005")
                
                # 3. The EPC starts exactly 18 characters (9 bytes) into the packet
                # CC FF FF 20 05 10 00 30 00 [EPC...]
                epc_start = idx + 18
                epc_code = hex_str[epc_start:epc_start+24] # Grab 24 chars (12 bytes)
                
                # 4. Anti-spam: Only log to DB if we haven't seen it in the last 3 seconds
                current_time = time.time()
                if epc_code not in recent_tags or (current_time - recent_tags[epc_code]) > 3:
                    log_tag(epc_code)
                    recent_tags[epc_code] = current_time
                    
        time.sleep(0.05) # Give the CPU a tiny rest

except KeyboardInterrupt:
    print("\n>>> Shutting down tracker...")
    device.close()
    db.close()
except Exception as e:
    print(f"\n[CRITICAL ERROR] {e}")