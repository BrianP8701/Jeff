from dotenv import load_dotenv
import os
from openai import OpenAI
import tiktoken

load_dotenv()

client = OpenAI()

def num_tokens_from_string(string: str, model_name: str = "text-embedding-ada-002") -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def chunk_content(content: str, max_tokens: int = 5000) -> list[str]:
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for line in content.split('\n'):
        line_tokens = num_tokens_from_string(line)
        if current_tokens + line_tokens > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = line
            current_tokens = line_tokens
        else:
            current_chunk += line + '\n'
            current_tokens += line_tokens

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

if __name__ == "__main__":
    print(get_embedding("Hello, world!"))
