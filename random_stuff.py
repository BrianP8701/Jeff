import pandas as pd
from server.database.queries import create_link, get_link_by_url
from server.embeddings.embed import get_embedding, chunk_content

def process_and_store_history():
    data = pd.read_csv('links.csv')
    for index, row in data.iterrows():
        url = row['url']  # Assuming the URL is the second item in the entry tuple
        title = row['title']  # Assuming the title is the third item in the entry tuple

        existing_link = get_link_by_url(url)
        if existing_link:
            print(f"Link already exists: {url}")
            continue
        
        try:
            content = row['content']
            chunks = chunk_content(content)

            for i, chunk in enumerate(chunks):
                chunk = "This is a webpage: \n" + chunk
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

process_and_store_history()