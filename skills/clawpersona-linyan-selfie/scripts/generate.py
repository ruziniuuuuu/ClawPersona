#!/usr/bin/env python3
"""Generate Lin Yan (professional) selfie via Doubao Seedream API."""
import os, base64, argparse, urllib.request
from openai import OpenAI

# 林妍 - 干练知性投行经理
REF_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")
OUT_DIR = os.path.expanduser("~/.openclaw/media")

MODES = {
    "mirror": "photo of this professional woman taking a mirror selfie, {prompt}, full body visible, confident pose, modern office background, sophisticated lighting, elegant business attire",
    "selfie": "close-up selfie of this professional woman, {prompt}, natural angle, confident expression, professional makeup, sleek and polished look, corporate setting",
    "photo": "photo of this professional woman, {prompt}, professional lighting, realistic, confident posture, business casual or formal setting, sharp and polished",
}

def main():
    parser = argparse.ArgumentParser(description="Generate Lin Yan professional selfies")
    parser.add_argument("--prompt", required=True, help="Scene or outfit description")
    parser.add_argument("--mode", default="photo", choices=list(MODES.keys()), help="Photo mode")
    parser.add_argument("--filename", default="linyan.jpg", help="Output filename")
    parser.add_argument("--to", default=None, help="iMessage recipient")
    args = parser.parse_args()

    if not os.path.exists(REF_IMAGE):
        print(f"Error: Reference image not found: {REF_IMAGE}")
        exit(1)

    prompt = MODES[args.mode].format(prompt=args.prompt)

    with open(REF_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(
        timeout=300,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.environ.get("ARK_API_KEY"),
    )
    
    try:
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="1920x1920",
            response_format="url",
            extra_body={"image": f"data:image/jpeg;base64,{b64}", "watermark": False}
        )

        out_path = os.path.join(OUT_DIR, args.filename)
        urllib.request.urlretrieve(resp.data[0].url, out_path)
        
        if args.to:
            import subprocess
            r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
            if r.returncode != 0:
                print(f"MEDIA: {out_path}")
            else:
                print(f"sent: {out_path}")
        else:
            print(f"MEDIA: {out_path}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
