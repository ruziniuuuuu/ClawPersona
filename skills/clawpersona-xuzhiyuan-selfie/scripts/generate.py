#!/usr/bin/env python3
"""Generate Xu Zhiyuan (mysterious artist) selfie via Doubao Seedream API."""
import os, base64, argparse, urllib.request
from openai import OpenAI

REF_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")
OUT_DIR = os.path.expanduser("~/.openclaw/media")

MODES = {
    "mirror": "photo of this mysterious painter taking a mirror selfie, {prompt}, art studio with paintings background, paint stains on clothes, artistic lighting, contemplative mood",
    "selfie": "close-up selfie of this mysterious painter, {prompt}, intense gaze, paint on hands, studio background, dramatic artistic lighting, deep and soulful",
    "photo": "photo of this mysterious painter, {prompt}, thoughtful pose, gallery or riverside at sunset, golden hour lighting, mysterious and romantic expression",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--mode", default="photo", choices=list(MODES.keys()))
    parser.add_argument("--filename", default="xuzhiyuan.jpg")
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
