import sqlite3
import time
from datetime import datetime, timedelta

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('/Users/yush/Library/Application Support/Google/Chrome/Default/History')

# Create a cursor object
cur = conn.cursor()

def datetime_to_nanoseconds(dt):
    # WebKit-like epoch starts at January 1, 1601
    epoch_start = datetime(1601, 1, 1)
    
    # Get the difference between the datetime and the epoch start
    one_week_ago = dt - timedelta(weeks=1)
    delta = one_week_ago - epoch_start
    
    
    # Convert the difference to nanoseconds
    return int(delta.total_seconds() * 1e6)

# Example usage
dt = datetime.utcnow()
nanoseconds = datetime_to_nanoseconds(dt)

# Get the current tim
cur.execute(f'''SELECT * FROM urls WHERE last_visit_time >= {nanoseconds} ORDER BY last_visit_time DESC''')

# Example: Insert data
# cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")

# Commit the changes
# conn.commit()

# Query the data
# cur.execute("SELECT * FROM users")
rows = cur.fetchall()
print(len(rows))
for row in rows[0:10]:
    print(row)
    row

# Close the connection
conn.close()

13370211223604806
13370205955773581