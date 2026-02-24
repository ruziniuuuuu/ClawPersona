#!/usr/bin/env python3
"""Generate base images for all 5 male personas using Doubao text-to-image API."""
import os, urllib.request
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

HANDSOME = (
    "extremely handsome, strikingly attractive, perfect facial features, flawless skin, "
    "defined jawline, deep expressive eyes, tall and well-built, youthful appearance, "
    "Korean-Chinese idol-level looks, male model quality, charismatic presence, "
)

PERSONAS = {
    "domineering-ceo": (
        f"{HANDSOME}"
        "Chinese man, 28 years old, wearing a perfectly tailored dark charcoal suit with a silk tie, "
        "standing in a modern executive office with floor-to-ceiling windows overlooking a city skyline, "
        "confident and intense gaze, sharp and powerful aura, cinematic lighting, "
        "8k quality, photorealistic, portrait photography"
    ),
    "musician": (
        f"{HANDSOME}"
        "Chinese man, 24 years old, slightly long styled dark hair, wearing a cozy oversized knit sweater, "
        "holding an acoustic guitar, sitting in a warmly lit music studio, "
        "soft melancholic expression, dreamy and poetic atmosphere, warm bokeh background, "
        "8k quality, photorealistic, portrait photography"
    ),
    "doctor": (
        f"{HANDSOME}"
        "Chinese man, 27 years old, wearing a clean white doctor's coat over a light blue shirt, "
        "standing in a bright modern hospital, gentle and warm smile, "
        "professional yet approachable, soft natural lighting, "
        "8k quality, photorealistic, portrait photography"
    ),
    "sunshine-student": (
        f"{HANDSOME}"
        "Chinese young man, 21 years old, bright sunny smile, athletic toned physique, "
        "wearing a casual streetwear outfit, standing on a university campus, "
        "vibrant and energetic, natural sunlight, fresh and lively, "
        "8k quality, photorealistic, portrait photography"
    ),
    "mysterious-artist": (
        f"{HANDSOME}"
        "Chinese man, 26 years old, slightly disheveled dark hair, wearing a dark turtleneck, "
        "standing in a dimly lit art studio surrounded by large canvases, "
        "deep soulful gaze, moody dramatic side lighting, enigmatic and romantic, "
        "8k quality, photorealistic, portrait photography"
    ),
}

BASE_DIR = os.path.join(os.path.dirname(__file__), "../personas/male")

for persona, prompt in PERSONAS.items():
    out_path = os.path.join(BASE_DIR, persona, "base.jpg")
    print(f"Generating {persona}...")
    try:
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="1920x1920",
            response_format="url",
            extra_body={"watermark": False},
        )
        urllib.request.urlretrieve(resp.data[0].url, out_path)
        print(f"  Saved: {out_path}")
    except Exception as e:
        print(f"  Error: {e}")
