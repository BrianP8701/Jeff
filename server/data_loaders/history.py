import sqlite3
import time
from datetime import datetime, timedelta
from server.database.queries import create_link, get_link_by_url
from server.embeddings.embed import get_embedding, chunk_content
from server.apis.exa_client import get_contents_for_url

def get_history(base_name = 'brianprzezdziecki'):
      # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(f'/Users/{base_name}/Library/Application Support/Google/Chrome/Default/History')

    # Create a cursor object
    cur = conn.cursor()

    def datetime_to_nanoseconds(dt, weeks=1):
        # WebKit-like epoch starts at January 1, 1601
        epoch_start = datetime(1601, 1, 1)
        
        # Get the difference between the datetime and the epoch start
        one_week_ago = dt - timedelta(weeks)
        delta = one_week_ago - epoch_start
        
        
        # Convert the difference to nanoseconds
        return int(delta.total_seconds() * 1e6)

    # Example usage
    dt = datetime(2024, 8, 22)
    nanoseconds = datetime_to_nanoseconds(dt, weeks=2)
    today_nanoseconds = datetime_to_nanoseconds(datetime(2024, 8, 22))
    print(nanoseconds, today_nanoseconds)

    # Get the current tim
    cur.execute(f'''SELECT * FROM urls WHERE last_visit_time >= {nanoseconds} AND last_visit_time <= {today_nanoseconds} ORDER BY last_visit_time DESC''')

    # Example: Insert data
    # cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")

    # Commit the changes
    # conn.commit()

    # Query the data
    # cur.execute("SELECT * FROM users")
    rows = cur.fetchall()

    # Close the connection
    conn.close()
    return rows

def process_and_store_history(history_entries):
    for entry in history_entries:
        url = entry[1]  # Assuming the URL is the second item in the entry tuple
        title = entry[2]  # Assuming the title is the third item in the entry tuple

        existing_link = get_link_by_url(url)
        if existing_link:
            print(f"Link already exists: {url}")
            continue

        try:
            content = get_contents_for_url(url)
            chunks = chunk_content(content)

            for i, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)

                link_data = {
                    "url": url,
                    "title": f"{title} (chunk {i+1}/{len(chunks)})",
                    "content": chunk,
                    "embedding": embedding
                }

                stored_link = create_link(link_data)
                print(f"Stored link chunk: {stored_link.id} - {stored_link.title}")
        except Exception as e:
            print(f"Error processing link {url}: {e}")
