import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url = "https://api.exa.ai/contents"


def get_contents_for_url(web_url):
    global url
    payload = {
        "ids": [web_url],
        "text": {"includeHtmlTags": False},
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": os.getenv("EXA_KEY"),
    }

    response = requests.post(url, json=payload, headers=headers)
    content = json.loads(response.text)
    # print(content.results.text)
    return content['results'][0]['text']
