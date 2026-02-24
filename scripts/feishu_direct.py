#!/usr/bin/env python3
"""
Feishu message sender for ClawPersona - Direct API version
Uses OpenClaw's message tool to send images directly to Feishu
"""
import os
import subprocess
import sys
from typing import Optional

def send_image_to_feishu(image_path: str, chat_id: Optional[str] = None, caption: Optional[str] = None) -> bool:
    """
    Send an image to Feishu using OpenClaw's message tool
    
    Args:
        image_path: Path to the image file
        chat_id: Feishu chat ID (optional, defaults to current chat from env)
        caption: Optional caption text
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        return False
    
    # Get chat ID from environment or use provided
    # Try multiple environment variables that might contain the chat ID
    target = chat_id 
    if not target:
        # Try to get from various environment variables
        for env_var in ["FEISHU_CHAT_ID", "OPENCLAW_CONVERSATION_ID", "FEISHU_TARGET"]:
            target = os.environ.get(env_var)
            if target:
                break
    
    # If still no target, try to extract from session key
    if not target:
        session_key = os.environ.get("OPENCLAW_SESSION_KEY", "")
        if "feishu:group:" in session_key:
            # Extract chat ID from session key like "agent:main:feishu:group:oc_xxx"
            parts = session_key.split(":")
            if len(parts) >= 4:
                target = parts[-1]
    
    if not target:
        # Try to get from parent process environment
        try:
            with open(f"/proc/{os.getppid()}/environ", "rb") as f:
                parent_env = f.read().decode("utf-8", errors="ignore")
                for line in parent_env.split("\0"):
                    if line.startswith("FEISHU_CHAT_ID="):
                        target = line.split("=", 1)[1]
                        break
                    elif line.startswith("OPENCLAW_CONVERSATION_ID="):
                        target = line.split("=", 1)[1]
                        break
        except:
            pass
    
    if not target:
        print(f"Warning: No chat ID found, outputting MEDIA format", file=sys.stderr)
        print(f"MEDIA: {image_path}")
        return False
    
    # Use openclaw message tool to send
    try:
        # Build the command
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", target,
            "--media", image_path
        ]
        
        if caption:
            cmd.extend(["--message", caption])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Image sent to Feishu: {image_path}")
            return True
        else:
            print(f"Failed to send image: {result.stderr}", file=sys.stderr)
            print(f"MEDIA: {image_path}")
            return False
            
    except Exception as e:
        print(f"Error sending image: {e}", file=sys.stderr)
        print(f"MEDIA: {image_path}")
        return False


def send_text_to_feishu(text: str, chat_id: Optional[str] = None) -> bool:
    """Send text message to Feishu."""
    target = chat_id or os.environ.get("FEISHU_CHAT_ID") or os.environ.get("OPENCLAW_CONVERSATION_ID")
    
    if not target:
        print(text)
        return False
    
    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", target,
            "--message", text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error sending text: {e}", file=sys.stderr)
        print(text)
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send media to Feishu via OpenClaw")
    parser.add_argument("--image", help="Image path to send")
    parser.add_argument("--text", help="Text message")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    args = parser.parse_args()
    
    if args.image:
        send_image_to_feishu(args.image, args.chat_id, args.text)
    elif args.text:
        send_text_to_feishu(args.text, args.chat_id)
    else:
        print("Usage: python3 feishu_direct.py --image path.jpg [--text 'caption'] [--chat-id id]")
