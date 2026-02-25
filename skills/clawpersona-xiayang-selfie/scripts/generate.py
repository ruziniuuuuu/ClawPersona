#!/usr/bin/env python3
"""Generate Xia Yang (sporty) selfie via Doubao Seedream API."""
import os, base64, argparse, urllib.request
from openai import OpenAI

REF_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")
OUT_DIR = os.path.expanduser("~/.openclaw/media")

MODES = {
    "mirror": "photo of this athletic fitness trainer taking a mirror selfie, {prompt}, gym or outdoor workout background, sports wear, energetic pose, bright lighting",
    "selfie": "close-up selfie of this athletic fitness trainer, {prompt}, bright smile, sweat glowing, gym or nature background, vibrant and healthy energy",
    "photo": "photo of this athletic fitness trainer, {prompt}, dynamic pose, gym or sports field, sunny lighting, energetic and motivating expression",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--mode", default="photo", choices=list(MODES.keys()))
    parser.add_argument("--filename", default="xiayang.jpg")
    args = parser.parse_args()

    if not os.path.exists(REF_IMAGE):
        print(f"Error: Reference image not found: {REF_IMAGE}"); exit(1)

    prompt = MODES[args.mode].format(prompt=args.prompt)
    with open(REF_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(
        timeout=300, base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.environ.get("ARK_API_KEY"))
    
    try:
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128", prompt=prompt, size="1920x1920",
            response_format="url", extra_body={"image": f"data:image/jpeg;base64,{b64}", "watermark": False})
        
        out_path = os.path.join(OUT_DIR, args.filename)
        urllib.request.urlretrieve(resp.data[0].url, out_path)
        
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
        try:
            from feishu import is_feishu_env, send_media
            if is_feishu_env() and send_media(out_path):
                print("[已发送到飞书]")
            else:
                print(f"MEDIA: {out_path}")
        except:
            print(f"MEDIA: {out_path}")
    except Exception as e:
        print(f"Error: {e}"); exit(1)

if __name__ == "__main__":
    main()
