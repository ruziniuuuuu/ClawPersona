#!/usr/bin/env python3
"""Generate voice greeting using edge-tts for current persona."""
import os, sys, argparse

# Persona voice configs
VOICE_CONFIGS = {
    "suwan":       {"voice": "zh-CN-XiaoxiaoNeural", "rate": "-10%"},
    "linyan":      {"voice": "zh-CN-XiaoyiNeural",   "rate": "-5%"},
    "gujin":       {"voice": "zh-CN-XiaoyiNeural",   "rate": "-5%"},
    "xiayang":     {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+5%"},
    "tangguo":     {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+10%"},
    "lushenchen":  {"voice": "zh-CN-YunjianNeural",  "rate": "-10%"},
    "jiangyu":     {"voice": "zh-CN-YunxiNeural",    "rate": "-10%"},
    "shenmobai":   {"voice": "zh-CN-YunxiNeural",    "rate": "-8%"},
    "guyan":       {"voice": "zh-CN-YunfengNeural",  "rate": "+5%"},
    "xuzhiyuan":   {"voice": "zh-CN-YunjianNeural",  "rate": "-15%"},
}

OUT_DIR = os.path.expanduser("~/.openclaw/media")

def main():
    parser = argparse.ArgumentParser(description="Generate persona voice greeting")
    parser.add_argument("--persona", required=True, help="Persona key (e.g. linyan)")
    parser.add_argument("--text", required=True, help="Text to speak")
    parser.add_argument("--filename", default="voice.mp3", help="Output filename")
    args = parser.parse_args()

    cfg = VOICE_CONFIGS.get(args.persona)
    if not cfg:
        print(f"Error: Unknown persona '{args.persona}'")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, args.filename)

    import asyncio
    import edge_tts

    async def generate():
        communicate = edge_tts.Communicate(args.text, cfg["voice"], rate=cfg["rate"])
        await communicate.save(out_path)

    asyncio.run(generate())
    print(f"MEDIA: {out_path}")

if __name__ == "__main__":
    main()
