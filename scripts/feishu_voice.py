#!/usr/bin/env python3
"""
Feishu voice sender for ClawPersona
Generates voice using Edge TTS and sends to Feishu
"""
import os
import subprocess
import sys
from typing import Optional

# Persona voice configurations
PERSONA_VOICES = {
    "suwan": "zh-CN-XiaoxiaoNeural",      # 苏婉 - 温柔女声
    "linyan": "zh-CN-XiaoyiNeural",       # 林妍 - 成熟知性女声
    "gujin": "zh-CN-XiaoyiNeural",        # 顾瑾 - 知性女声
    "xiayang": "zh-CN-XiaoxiaoNeural",    # 夏阳 - 活泼女声
    "tangguo": "zh-CN-XiaoxiaoNeural",    # 糖果 - 可爱女声
    "lushenchen": "zh-CN-YunxiNeural",    # 陆景深 - 男声
    "jiangyu": "zh-CN-YunxiNeural",       # 江屿 - 男声
    "shenmobai": "zh-CN-YunxiNeural",     # 沈墨白 - 男声
    "guyan": "zh-CN-YunxiNeural",         # 顾言 - 男声
    "xuzhiyuan": "zh-CN-YunxiNeural",     # 许知远 - 男声
}

def generate_voice(text: str, persona: str, output_path: str) -> bool:
    """
    Generate voice using Edge TTS
    
    Args:
        text: Text to convert to speech
        persona: Persona key (e.g., 'linyan', 'tangguo')
        output_path: Output file path (should be .mp3 or .opus)
    
    Returns:
        True if successful, False otherwise
    """
    voice = PERSONA_VOICES.get(persona, "zh-CN-XiaoxiaoNeural")
    
    try:
        # Use edge-tts to generate voice
        cmd = [
            "python3", "-m", "edge_tts",
            "--voice", voice,
            "--text", text,
            "--write-media", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"Voice generation failed: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error generating voice: {e}", file=sys.stderr)
        return False


def send_voice_to_feishu(voice_path: str, chat_id: Optional[str] = None) -> bool:
    """
    Send voice/audio to Feishu using OpenClaw's message tool
    
    Args:
        voice_path: Path to the audio file
        chat_id: Feishu chat ID (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not os.path.exists(voice_path):
        print(f"Error: Voice file not found: {voice_path}", file=sys.stderr)
        return False
    
    # Get chat ID from environment or use provided
    target = chat_id
    if not target:
        for env_var in ["FEISHU_CHAT_ID", "OPENCLAW_CONVERSATION_ID", "FEISHU_TARGET"]:
            target = os.environ.get(env_var)
            if target:
                break
    
    # Try to extract from session key
    if not target:
        session_key = os.environ.get("OPENCLAW_SESSION_KEY", "")
        if "feishu:group:" in session_key:
            parts = session_key.split(":")
            if len(parts) >= 4:
                target = parts[-1]
    
    # Try parent process environment
    if not target:
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
        print(f"Warning: No chat ID found, cannot send voice", file=sys.stderr)
        return False
    
    # Use openclaw message tool to send
    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", target,
            "--media", voice_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Voice sent to Feishu: {voice_path}")
            return True
        else:
            print(f"Failed to send voice: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error sending voice: {e}", file=sys.stderr)
        return False


def generate_and_send_voice(text: str, persona: str, chat_id: Optional[str] = None) -> bool:
    """
    Generate voice and send to Feishu
    
    Args:
        text: Text to convert to speech
        persona: Persona key
        chat_id: Feishu chat ID (optional)
    
    Returns:
        True if successful, False otherwise
    """
    # Generate output path
    out_dir = os.path.expanduser("~/.openclaw/media")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{persona}_voice.mp3")
    
    # Generate voice
    if not generate_voice(text, persona, output_path):
        return False
    
    # Send to Feishu
    return send_voice_to_feishu(output_path, chat_id)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate and send voice to Feishu")
    parser.add_argument("--text", required=True, help="Text to convert to speech")
    parser.add_argument("--persona", default="linyan", help="Persona key")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    parser.add_argument("--output", help="Output file path (optional)")
    args = parser.parse_args()
    
    if args.output:
        # Just generate, don't send
        success = generate_voice(args.text, args.persona, args.output)
        print(f"Generated: {args.output}" if success else "Failed")
    else:
        # Generate and send
        success = generate_and_send_voice(args.text, args.persona, args.chat_id)
        print("Sent successfully" if success else "Failed")
