from src.config import settings
from openai import OpenAI

# Initialize client with your API key from .env
c = OpenAI(api_key=settings.openai_api_key)

# Make a simple call for one product
r = c.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "Return ONLY one JSON object with keys brand, manufacturer, confidence (0..1). "
                "No prose, no explanations, no code fences."
            ),
        },
        {
            "role": "user",
            "content": 'Product name: "NISSIN BOWL NOODLE HOT & SPICE BEEF"',
        },
    ],
    temperature=0,
    response_format={"type": "json_object"},
)

print("RAW:", r.choices[0].message.content)
