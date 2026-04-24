import csv
import pymysql
import os
from dotenv import load_dotenv

# Load your database credentials
load_dotenv()

CSV_FILE = 'books.csv'
TABLE_NAME = 'books' # Change this if your table is named something else

print(">>> READING CSV FILE...")
books_data = []
try:
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        for row in reader:
            books_data.append(row)
except Exception as e:
    print(f"❌ Failed to read CSV: {e}")
    exit()

print(">>> CONNECTING TO DATABASE...")
try:
    db = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD") or "",
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor()
except Exception as e:
    print(f"❌ DATABASE CONNECTION FAILED: {e}")
    exit()

try:
    # 1. EXTRACT ALL IDs FROM THE CSV
    # (Assuming your primary key column in the CSV is literally called 'id')
    csv_ids = [row['epc'] for row in books_data if 'epc' in row]
    
    if not csv_ids:
        print("❌ CRITICAL: Could not find an 'id' column in the CSV.")
        exit()

    # 2. DELETE OLD ENTRIES
    # Delete any book in the database whose ID is NOT in the CSV
    format_strings = ','.join(['%s'] * len(csv_ids))
    delete_query = f"DELETE FROM {TABLE_NAME} WHERE id NOT IN ({format_strings})"
    cursor.execute(delete_query, tuple(csv_ids))
    deleted_count = cursor.rowcount
    print(f">>> Removed {deleted_count} old entries from the database.")

    # 3. INSERT OR UPDATE CURRENT ENTRIES
    columns = ', '.join(headers)
    placeholders = ', '.join(['%s'] * len(headers))
    
    # This creates the "ON DUPLICATE KEY UPDATE title=VALUES(title), etc..." logic
    updates = ', '.join([f"{col}=VALUES({col})" for col in headers if col != 'id'])
    
    insert_query = f"""
        INSERT INTO {TABLE_NAME} ({columns}) 
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {updates};
    """
    
    for row in books_data:
        values = tuple(row[col] for col in headers)
        cursor.execute(insert_query, values)

    # 4. COMMIT TO THE DATABASE
    db.commit()
    print(f"✅ SUCCESS: Synced {len(books_data)} books with the database!")

except Exception as e:
    db.rollback()
    print(f"❌ SQL ERROR: {e}")
finally:
    db.close()