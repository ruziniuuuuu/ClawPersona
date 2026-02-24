#!/usr/bin/env python3
"""
Unified Feishu media sender for ClawPersona
Handles sending images and voice messages to Feishu in all environments
"""
import os
import sys
import subprocess
from typing import Optional

def get_chat_id() -> Optional[str]:
    """Get Feishu chat ID from various sources"""
    # Try environment variables
    for env_var in ["FEISHU_CHAT_ID", "OPENCLAW_CONVERSATION_ID", "FEISHU_TARGET"]:
        chat_id = os.environ.get(env_var)
        if chat_id:
            return chat_id
    
    # Try to extract from session key
    session_key = os.environ.get("OPENCLAW_SESSION_KEY", "")
    if "feishu:group:" in session_key:
        parts = session_key.split(":")
        if len(parts) >= 4:
            return parts[-1]
    
    # Try parent process environment
    try:
        with open(f"/proc/{os.getppid()}/environ", "rb") as f:
            parent_env = f.read().decode("utf-8", errors="ignore")
            for line in parent_env.split("\0"):
                if line.startswith("FEISHU_CHAT_ID="):
                    return line.split("=", 1)[1]
                elif line.startswith("OPENCLAW_CONVERSATION_ID="):
                    return line.split("=", 1)[1]
    except:
        pass
    
    return None


def is_feishu_env() -> bool:
    """Check if running in Feishu environment"""
    return (
        os.environ.get("OPENCLAW_CHANNEL") == "feishu" or
        os.environ.get("FEISHU_CHAT_ID") or
        os.environ.get("OPENCLAW_CONVERSATION_ID") or
        "feishu" in os.environ.get("OPENCLAW_SESSION_KEY", "")
    )


def send_media_to_feishu(media_path: str, chat_id: Optional[str] = None) -> bool:
    """
    Send media (image or audio) to Feishu
    
    Args:
        media_path: Path to media file
        chat_id: Feishu chat ID (optional, will auto-detect)
    
    Returns:
        True if sent successfully
    """
    if not os.path.exists(media_path):
        print(f"Error: Media file not found: {media_path}", file=sys.stderr)
        return False
    
    # Get chat ID
    target = chat_id or get_chat_id()
    if not target:
        print(f"Warning: No chat ID found for Feishu", file=sys.stderr)
        return False
    
    # Use openclaw message tool to send
    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", target,
            "--media", media_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Media sent to Feishu: {media_path}")
            return True
        else:
            print(f"Failed to send media: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error sending media: {e}", file=sys.stderr)
        return False


def handle_media_output(media_path: str, chat_id: Optional[str] = None) -> str:
    """
    Handle media output - send to Feishu if in Feishu environment,
    otherwise output MEDIA format
    
    Args:
        media_path: Path to media file
        chat_id: Optional chat ID
    
    Returns:
        Output string for display
    """
    if is_feishu_env():
        success = send_media_to_feishu(media_path, chat_id)
        if success:
            return f"[已发送到飞书]"
    
    # Fallback to MEDIA format
    return f"MEDIA: {media_path}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send media to Feishu")
    parser.add_argument("media_file", help="Path to media file")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    args = parser.parse_args()
    
    result = handle_media_output(args.media_file, args.chat_id)
    print(result)
