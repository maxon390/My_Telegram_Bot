import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Тягне ваш ключ із .env

# Ініціалізація клієнта з ключем із системи
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Приклад запиту
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Привіт, як справи?"}]
)

print(response.choices[0].message.content)