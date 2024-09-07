import requests
import os

url = "https://github.com/BrianP8701/Jeff"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": os.getenv("EXA_KEY")
}

response = requests.post(url, headers=headers)

print(response.text)
