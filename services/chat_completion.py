from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def chat_response(model,PROMPT):
    completion =  client.chat.completions.create(
                    model=model,
                    messages=[{'role': "user","content" : PROMPT}]
                    )
    
    return completion.choices[0].message.content