import os
from openai import OpenAI
# Ініціалізація клієнта з ключем із системи
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Приклад запиту
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Привіт, як справи?"}]
    )
    print(response.choices[0].message.content)
except Exception:
    print("помилка")

