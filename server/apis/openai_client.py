from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def generate_answer_summary(question, content, model='gpt-4o-mini'):
    # Step 1: send the conversation and available functions to the model
    messages = [
        {
            "role": "user",
            "content": f"Answer the following question: {question}. Only use information from the following text and provide as brief of an answer as possible: \n {content}"
        }
    ]
    # print(messages)
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )
    # print(response)
    return response.choices[0].message.content