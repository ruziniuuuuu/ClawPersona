#!/usr/bin/env python3
"""
Feishu support for ClawPersona - Minimal version
Handles image and voice output for Feishu channel
"""
import os
import subprocess
import sys
from typing import Optional

# Persona voice mapping
PERSONA_VOICES = {
    "suwan": "zh-CN-XiaoxiaoNeural",
    "linyan": "zh-CN-XiaoyiNeural",
    "gujin": "zh-CN-XiaoyiNeural",
    "xiayang": "zh-CN-XiaoxiaoNeural",
    "tangguo": "zh-CN-XiaoxiaoNeural",
    "lushenchen": "zh-CN-YunxiNeural",
    "jiangyu": "zh-CN-YunxiNeural",
    "shenmobai": "zh-CN-YunxiNeural",
    "guyan": "zh-CN-YunxiNeural",
    "xuzhiyuan": "zh-CN-YunxiNeural",
}


def is_feishu_env() -> bool:
    """Check if running in Feishu environment"""
    return (
        os.environ.get("OPENCLAW_CHANNEL") == "feishu" or
        os.environ.get("FEISHU_CHAT_ID") or
        "feishu" in os.environ.get("OPENCLAW_SESSION_KEY", "")
    )


def get_chat_id() -> Optional[str]:
    """Get Feishu chat ID from environment"""
    for env_var in ["FEISHU_CHAT_ID", "OPENCLAW_CONVERSATION_ID"]:
        chat_id = os.environ.get(env_var)
        if chat_id:
            return chat_id
    
    # Try to extract from session key
    session_key = os.environ.get("OPENCLAW_SESSION_KEY", "")
    if "feishu:group:" in session_key:
        parts = session_key.split(":")
        if len(parts) >= 4:
            return parts[-1]
    return None


def send_media(media_path: str, caption: Optional[str] = None) -> bool:
    """Send media file to Feishu"""
    if not os.path.exists(media_path):
        return False
    
    chat_id = get_chat_id()
    if not chat_id:
        return False
    
    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", chat_id,
            "--media", media_path
        ]
        if caption:
            cmd.extend(["--message", caption])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except:
        return False


def handle_output(media_path: str, caption: Optional[str] = None) -> str:
    """Handle media output - send to Feishu or output MEDIA format"""
    if is_feishu_env() and send_media(media_path, caption):
        return "[已发送到飞书]"
    return f"MEDIA: {media_path}"


def generate_voice(text: str, persona: str, output_path: str) -> bool:
    """Generate voice using Edge TTS"""
    voice = PERSONA_VOICES.get(persona, "zh-CN-XiaoxiaoNeural")
    try:
        cmd = [
            "python3", "-m", "edge_tts",
            "--voice", voice,
            "--text", text,
            "--write-media", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0 and os.path.exists(output_path)
    except:
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", help="Media file to send")
    parser.add_argument("--voice", help="Text to generate voice")
    parser.add_argument("--persona", default="suwan")
    parser.add_argument("--caption", help="Caption for media")
    args = parser.parse_args()
    
    if args.voice:
        out_path = os.path.expanduser(f"~/.openclaw/media/{args.persona}_voice.mp3")
        if generate_voice(args.voice, args.persona, out_path):
            print(handle_output(out_path, args.caption))
        else:
            print("Failed to generate voice")
    elif args.media:
        print(handle_output(args.media, args.caption))
    else:
        print("Usage: python3 feishu.py --media path.jpg")
        print("       python3 feishu.py --voice 'Hello' --persona suwan")
