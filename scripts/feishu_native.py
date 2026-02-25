#!/usr/bin/env python3
"""
Native Feishu integration for ClawPersona
Provides seamless image and voice output support for Feishu channel
"""
import os
import sys
import subprocess
from typing import Optional, Dict, Any

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


def send_media_to_feishu(media_path: str, chat_id: Optional[str] = None, caption: Optional[str] = None) -> bool:
    """
    Send media (image or audio) to Feishu natively
    
    Args:
        media_path: Path to media file
        chat_id: Feishu chat ID (optional, will auto-detect)
        caption: Optional caption text for images
    
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
        
        if caption:
            cmd.extend(["--message", caption])
        
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


def handle_media_output(media_path: str, chat_id: Optional[str] = None, caption: Optional[str] = None) -> str:
    """
    Handle media output - send to Feishu if in Feishu environment,
    otherwise output MEDIA format
    
    Args:
        media_path: Path to media file
        chat_id: Optional chat ID
        caption: Optional caption text
    
    Returns:
        Output string for display
    """
    if is_feishu_env():
        success = send_media_to_feishu(media_path, chat_id, caption)
        if success:
            return f"[已发送到飞书]"
    
    # Fallback to MEDIA format
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
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"Voice generation failed: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error generating voice: {e}", file=sys.stderr)
        return False


def convert_to_opus(input_path: str, output_path: str) -> bool:
    """Convert MP3 to Opus format for Feishu native voice"""
    try:
        # Check if ffmpeg is available
        result = subprocess.run(["which", "ffmpeg"], capture_output=True)
        if result.returncode != 0:
            print("Warning: ffmpeg not found, using MP3 format", file=sys.stderr)
            return False
        
        # Convert to opus
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:a", "libopus",
            "-b:a", "24k",
            "-vbr", "on",
            "-compression_level", "10",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"Opus conversion failed: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error converting to opus: {e}", file=sys.stderr)
        return False


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
    
    # Estimate based on file size (rough approximation for opus)
    file_size = os.path.getsize(file_path)
    return int((file_size * 8 / 24000) * 1000)


def send_voice_to_feishu(voice_path: str, persona: str, text: str, chat_id: Optional[str] = None) -> bool:
    """
    Send voice message to Feishu in native format (playable directly)
    
    Args:
        voice_path: Path to voice file (MP3 or Opus)
        persona: Persona key for voice attribution
        text: Original text (for context)
        chat_id: Feishu chat ID (optional)
    
    Returns:
        True if sent successfully
    """
    if not os.path.exists(voice_path):
        print(f"Error: Voice file not found: {voice_path}", file=sys.stderr)
        return False
    
    # Convert to opus if needed
    opus_path = voice_path
    if voice_path.endswith('.mp3'):
        opus_path = voice_path.replace('.mp3', '.opus')
        if not convert_to_opus(voice_path, opus_path):
            opus_path = voice_path  # Fallback to original
    
    # Send as media
    return send_media_to_feishu(opus_path, chat_id)


def generate_and_send_voice(text: str, persona: str, chat_id: Optional[str] = None, 
                           output_dir: Optional[str] = None) -> bool:
    """
    Generate voice and send to Feishu
    
    Args:
        text: Text to convert to speech
        persona: Persona key
        chat_id: Feishu chat ID (optional)
        output_dir: Output directory (default: ~/.openclaw/media)
    
    Returns:
        True if successful
    """
    if output_dir is None:
        output_dir = os.path.expanduser("~/.openclaw/media")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate MP3
    mp3_path = os.path.join(output_dir, f"{persona}_voice.mp3")
    
    if not generate_voice(text, persona, mp3_path):
        return False
    
    # Send to Feishu
    success = send_voice_to_feishu(mp3_path, persona, text, chat_id)
    
    return success


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Native Feishu integration for ClawPersona")
    parser.add_argument("--media", help="Media file to send")
    parser.add_argument("--voice-text", help="Text to convert to voice")
    parser.add_argument("--persona", default="linyan", help="Persona key for voice")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    parser.add_argument("--caption", help="Caption for images")
    args = parser.parse_args()
    
    if args.voice_text:
        success = generate_and_send_voice(args.voice_text, args.persona, args.chat_id)
        print("Voice sent successfully" if success else "Failed to send voice")
    elif args.media:
        result = handle_media_output(args.media, args.chat_id, args.caption)
        print(result)
    else:
        print("Usage: python3 feishu_native.py --media path.jpg [--caption 'text']")
        print("       python3 feishu_native.py --voice-text 'Hello' --persona linyan")
