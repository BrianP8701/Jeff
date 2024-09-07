from server.data_loaders.history import get_history
from server.apis.exa_client import get_contents_for_url
from server.database.queries import *

history = get_history()
# index 1 has the url and index 2 has the title

for row in history:
    url = row[1]
    title = row[2]
    content = get_contents_for_url(row[1])
    link_data = {
        "url": url,
        "title": title,
        "content": content,
    }
    create_link(link_data)
