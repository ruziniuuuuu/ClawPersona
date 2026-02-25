#!/usr/bin/env python3
"""Generate Guyan (sunshine student) selfie via Doubao Seedream API."""
import os, base64, argparse, urllib.request
from openai import OpenAI

REF_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")
OUT_DIR = os.path.expanduser("~/.openclaw/media")

MODES = {
    "mirror": "photo of this energetic college athlete taking a mirror selfie, {prompt}, sporty outfit, bright smile, athletic build, youthful energy, realistic photography",
    "selfie": "close-up selfie of this energetic college athlete, {prompt}, bright sunny smile, youthful and handsome, sporty vibe, natural lighting, realistic photography",
    "photo": "photo of this energetic college athlete, {prompt}, basketball court or campus setting, athletic and lively, sunshine and energy, realistic photography",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--mode", default="photo", choices=list(MODES.keys()))
    parser.add_argument("--filename", default="guyan.jpg")
    parser.add_argument("--to", default=None)
    args = parser.parse_args()

    if not os.path.exists(REF_IMAGE):
        print(f"Error: Reference image not found: {REF_IMAGE}"); exit(1)

    prompt = MODES[args.mode].format(prompt=args.prompt)
    with open(REF_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(
        timeout=300,base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=os.environ.get("ARK_API_KEY"))
    try:
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128", prompt=prompt, size="1920x1920",
            response_format="url", extra_body={"image": f"data:image/jpeg;base64,{b64}", "watermark": False}
        )
        out_path = os.path.join(OUT_DIR, args.filename)
        urllib.request.urlretrieve(resp.data[0].url, out_path)
        
        # Send or output media
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
        try:
            from feishu_media import is_feishu_env, send_media_to_feishu
            
            if args.to and (args.to.startswith("+") or args.to.isdigit()):
                import subprocess
                r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
                print(f"sent: {out_path}" if r.returncode == 0 else f"MEDIA: {out_path}")
            elif is_feishu_env():
                success = send_media_to_feishu(out_path)
                print(f"[已发送到飞书]" if success else f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")
        except Exception:
            print(f"MEDIA: {out_path}")
    except Exception as e:
        print(f"Error: {e}"); exit(1)

if __name__ == "__main__":
    main()
