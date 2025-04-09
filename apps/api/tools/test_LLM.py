import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print(os.getenv("OPENAI_BASE_URL"))
print(os.getenv("OPENAI_API_KEY"))

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = "Give me some fun pool team name ideas for a team that sucks at pool"

response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1000
)

print(response.choices[0].message.content.strip())