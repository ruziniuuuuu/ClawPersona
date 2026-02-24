#!/usr/bin/env python3
"""Generate Xu Zhiyuan (mysterious artist) selfie via Doubao Seedream API."""
import os, base64, argparse, urllib.request
from openai import OpenAI

REF_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")
OUT_DIR = os.path.expanduser("~/.openclaw/media")

MODES = {
    "mirror": "photo of this mysterious painter taking a mirror selfie, {prompt}, dark turtleneck, brooding artistic vibe, paint-stained hands, moody lighting, realistic photography",
    "selfie": "close-up selfie of this mysterious painter, {prompt}, deep soulful eyes, enigmatic expression, artistic intensity, dramatic lighting, realistic photography",
    "photo": "photo of this mysterious painter, {prompt}, art studio or gallery setting, surrounded by canvases, moody atmospheric lighting, brooding and romantic, realistic photography",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--mode", default="photo", choices=list(MODES.keys()))
    parser.add_argument("--filename", default="xuzhiyuan.jpg")
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
        if args.to:
            import subprocess
            if args.to.startswith("+") or args.to.isdigit():
                r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
                print(f"MEDIA: {out_path}" if r.returncode != 0 else f"sent: {out_path}")
            elif args.to.startswith("feishu:"):
                webhook_url = args.to[7:]
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
                try:
                    from feishu_sender import send_to_feishu
                    send_to_feishu(out_path, None, webhook_url)
                except ImportError:
                    print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")
        else:
            if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
                try:
                    from feishu_direct import send_image_to_feishu
                    success = send_image_to_feishu(out_path)
                    if not success:
                        from feishu_adapter import adapt_for_feishu
                        print(adapt_for_feishu(out_path))
                except ImportError:
                    try:
                        from feishu_adapter import adapt_for_feishu
                        print(adapt_for_feishu(out_path))
                    except ImportError:
                        print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")
    except Exception as e:
        print(f"Error: {e}"); exit(1)

if __name__ == "__main__":
    main()
