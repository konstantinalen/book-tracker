import hid
import time
import pymysql
import os
import socket
from dotenv import load_dotenv

# Load the variables from your .env file
load_dotenv()

# Database Connection
try:
    db = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD") or "",
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor()
except Exception as e:
    print(f">>> FAILED TO CONNECT TO DATABASE: {e}")
    exit()

def log_tag(epc_string, reader_name):
    print(f"\n>>> PROCESSING TAG: {epc_string}")
    try:
        cursor.execute(
            "INSERT INTO scan_logs (epc, reader_name) VALUES (%s, %s)", 
            (epc_string, reader_name)
        )
        
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

# --- CONNECTION ROUTING ---
CONNECTION_MODE = os.getenv("CONNECTION_MODE", "USB").upper()
print("--- LIBRARY INVENTORY TRACKER ONLINE ---")
print(f">>> Mode: {CONNECTION_MODE}")

try:
    # 1. Open the correct pipeline based on the .env file
    if CONNECTION_MODE == "WIFI":
        READER_IP = os.getenv("READER_IP")
        READER_PORT = int(os.getenv("READER_PORT", 49152))
        READER_NAME = "Hotspot_Wi-Fi_Scanner"
        
        print(f">>> Connecting to Reader at {READER_IP}:{READER_PORT}...")
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.settimeout(5.0) # Give up if it can't connect in 5 seconds
        tcp_client.connect((READER_IP, READER_PORT))
        tcp_client.setblocking(False) # Make it non-blocking so the loop doesn't freeze
        print(">>> SUCCESS: Wi-Fi TCP pipeline opened.")

    else:
        VID = 0x04D8
        PID = 0x033F
        READER_NAME = "Desk_USB_Scanner"
        
        print(">>> Connecting to USB Reader...")
        device = hid.device()
        device.open(VID, PID)
        device.set_nonblocking(1)
        print(">>> SUCCESS: USB HID pipeline opened.")

    print(">>> Listening for tags...\n")
    recent_tags = {}
    
    # 2. The Universal Listening Loop
    while True:
        hex_str = ""
        
        # Grab data from whichever pipe is open
        if CONNECTION_MODE == "WIFI":
            try:
                data = tcp_client.recv(1024)
                if data:
                    hex_str = data.hex().upper()
            except BlockingIOError:
                pass # Normal behavior, means no data has arrived yet
            except Exception as e:
                print(f"\n[NETWORK ERROR] {e}")
                break
        else:
            data = device.read(64)
            if data:
                hex_str = bytes(data).hex().upper()

        # 3. Parse the data (Identical for USB and Wi-Fi)
        if hex_str:
            if "CCFFFF2005" in hex_str:
                idx = hex_str.find("CCFFFF2005")
                epc_start = idx + 18
                epc_code = hex_str[epc_start:epc_start+24]
                
                current_time = time.time()
                if epc_code not in recent_tags or (current_time - recent_tags[epc_code]) > 3:
                    log_tag(epc_code, READER_NAME)
                    recent_tags[epc_code] = current_time
                    
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n>>> Shutting down tracker...")
except Exception as e:
    print(f"\n[CRITICAL ERROR] {e}")
finally:
    # Clean up whichever connections were opened
    if 'tcp_client' in locals(): tcp_client.close()
    if 'device' in locals(): device.close()
    db.close()