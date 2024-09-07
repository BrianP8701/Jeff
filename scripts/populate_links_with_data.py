from server.data_loaders.history import get_history
from server.apis.exa_client import get_contents_for_url
from server.database.queries import *

history = get_history()
# index 1 has the url and index 2 has the title
total = len(history)
print(f"total is {total}")
i = 0
failed_urls = []

for row in history:
    url = row[1]
    title = row[2]
    try:
        content = get_contents_for_url(row[1])
        link_data = {
			"url": url,
			"title": title,
			"content": content,
		}
        create_link(link_data)
  
    except Exception as e:
        print(url)
        print(e)
        failed_urls.append(row)
    
    i += 1
    if i % 50 == 0:
        print("\n\n\n\n\n")
        print("=======done status=======")
        print(f"{i} / {total} done")
        print("=======done end=======")

print("\n\n\n\n\n")
print("Failed urls")
print(failed_urls)