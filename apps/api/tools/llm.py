import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from parent folder
load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()
