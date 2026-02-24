#!/usr/bin/env python3
"""
Send native voice message to Feishu
Uses Feishu API directly to send audio as native voice message
"""
import os
import sys
import json
import subprocess
from typing import Optional

def get_chat_id() -> Optional[str]:
    """Get chat ID from various sources"""
    for env_var in ["FEISHU_CHAT_ID", "OPENCLAW_CONVERSATION_ID", "FEISHU_TARGET"]:
        chat_id = os.environ.get(env_var)
        if chat_id:
            return chat_id
    
    session_key = os.environ.get("OPENCLAW_SESSION_KEY", "")
    if "feishu:group:" in session_key:
        parts = session_key.split(":")
        if len(parts) >= 4:
            return parts[-1]
    
    return None


def get_audio_duration(file_path: str) -> int:
    """Get audio duration in milliseconds"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            duration_sec = float(result.stdout.strip())
            return int(duration_sec * 1000)
    except:
        pass
    
    # Estimate: ~24kbps for opus
    file_size = os.path.getsize(file_path)
    return int((file_size * 8 / 24000) * 1000)


def send_native_voice(voice_path: str, duration_ms: Optional[int] = None) -> bool:
    """
    Send native voice message to Feishu
    
    This uses the OpenClaw message tool with proper audio handling
    """
    if not os.path.exists(voice_path):
        print(f"Error: Voice file not found: {voice_path}", file=sys.stderr)
        return False
    
    chat_id = get_chat_id()
    if not chat_id:
        print("Error: No chat ID found", file=sys.stderr)
        return False
    
    if duration_ms is None:
        duration_ms = get_audio_duration(voice_path)
    
    # Use openclaw message tool
    # The key is to let OpenClaw handle the media type detection
    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", chat_id,
            "--media", voice_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Voice sent: {voice_path}")
            return True
        else:
            print(f"Failed: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send native voice to Feishu")
    parser.add_argument("voice_file", help="Path to voice file (opus or mp3)")
    parser.add_argument("--duration", type=int, help="Duration in milliseconds")
    args = parser.parse_args()
    
    success = send_native_voice(args.voice_file, args.duration)
    sys.exit(0 if success else 1)
