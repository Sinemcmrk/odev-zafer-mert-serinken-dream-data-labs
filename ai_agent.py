
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent

BRAND_FILES = {
    "aba_psikoloji": "aba_psikoloji.json",
    "aba_egitim": "aba_egitim.json",
    "e4i": "e4i.json",
    "design_house_global": "design_house_global.json",
}


def generate_post(brand_id, topic):
    # 1. Seçilen markanın dosyasını belirle
    if brand_id not in BRAND_FILES:
        raise ValueError("Geçersiz marka seçimi!")

    if not topic.strip():
        raise ValueError("Konu boş olamaz!")

    # 2. Brand Kit dosyasını oku
    brand_path = BASE_DIR / "brand_kits" / BRAND_FILES[brand_id]

    with open(brand_path, encoding="utf-8") as file:
        brand_kit = json.load(file)

    # 3. Post Library dosyasını oku
    with open(
        BASE_DIR / "post_library" / "posts.json",
        encoding="utf-8"
    ) as file:
        all_posts = json.load(file)

    # 4. Yalnızca seçilen markanın örneklerini al
    brand_posts = [
        post for post in all_posts
        if post["brand_id"] == brand_id
    ]

    # 5. Gemini API anahtarını yükle
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY bulunamadı!")

    client = genai.Client(api_key=api_key)

    # 6. Prompt oluştur
    prompt = f"""
You are an AI social media content assistant.

Generate ONE original Instagram post for the selected brand.

BRAND KIT:
{json.dumps(brand_kit, ensure_ascii=False)}

EXAMPLE POSTS:
{json.dumps(brand_posts, ensure_ascii=False)}

USER TOPIC:
{topic}

RULES:
- Follow the brand's language, tone, audience and content rules.
- Use example posts for inspiration without copying.
- Keep the headline short and suitable for an Instagram visual.
- Keep the body concise: 1-3 short sentences.
- Write a useful caption with a natural call to action.
- Do not invent statistics, sources, events or professional claims.
- For psychology topics, avoid diagnoses and guaranteed outcomes.
- Return only the requested JSON fields.
"""

    # 7. Gemini'den yapılandırılmış JSON çıktısı al
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "headline": {"type": "STRING"},
                    "body": {"type": "STRING"},
                    "caption": {"type": "STRING"},
                    "cta": {"type": "STRING"},
                    "hashtags": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": [
                    "headline",
                    "body",
                    "caption",
                    "cta",
                    "hashtags"
                ]
            }
        )
    )

    # 8. JSON metnini Python sözlüğüne dönüştür
    return json.loads(response.text)
