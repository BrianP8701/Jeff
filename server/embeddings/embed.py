from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI()

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    print(response)
    return response.data[0].embedding

if __name__ == "__main__":
    print(get_embedding("Hello, world!"))
