#!/usr/bin/env python3
"""
Feishu native voice message sender for ClawPersona
Generates voice using Edge TTS and converts to Feishu native format (opus)
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
            return int(duration_sec * 1000)  # Convert to milliseconds
    except:
        pass
    
    # Estimate based on file size (rough approximation)
    file_size = os.path.getsize(file_path)
    # Assume ~24kbps for opus
    return int((file_size * 8 / 24000) * 1000)


def send_native_voice_to_feishu(voice_path: str, duration_ms: int, chat_id: Optional[str] = None) -> bool:
    """
    Send native voice message to Feishu
    Uses OpenClaw's message tool with audio type
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
    
    if not target:
        print(f"Warning: No chat ID found, cannot send voice", file=sys.stderr)
        return False
    
    # Use openclaw message tool to send as audio
    try:
        # For native voice, we need to use the message tool with audio type
        # The message tool should handle the conversion
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


def generate_and_send_native_voice(text: str, persona: str, chat_id: Optional[str] = None) -> bool:
    """
    Generate voice and send as Feishu native voice message
    """
    out_dir = os.path.expanduser("~/.openclaw/media")
    os.makedirs(out_dir, exist_ok=True)
    
    # Generate MP3 first
    mp3_path = os.path.join(out_dir, f"{persona}_voice_temp.mp3")
    opus_path = os.path.join(out_dir, f"{persona}_voice.opus")
    
    if not generate_voice(text, persona, mp3_path):
        return False
    
    # Try to convert to opus for native voice format
    if convert_to_opus(mp3_path, opus_path):
        voice_path = opus_path
        duration_ms = get_audio_duration(opus_path)
    else:
        # Fallback to MP3
        voice_path = mp3_path
        duration_ms = get_audio_duration(mp3_path)
    
    # Send to Feishu
    success = send_native_voice_to_feishu(voice_path, duration_ms, chat_id)
    
    # Cleanup temp file
    if os.path.exists(mp3_path) and voice_path != mp3_path:
        os.remove(mp3_path)
    
    return success


def output_feishu_voice_format(voice_path: str, duration_ms: Optional[int] = None):
    """
    Output voice in Feishu native format for OpenClaw to handle
    This outputs a special format that OpenClaw Feishu channel will recognize
    """
    if not os.path.exists(voice_path):
        print(f"Error: Voice file not found: {voice_path}", file=sys.stderr)
        return
    
    if duration_ms is None:
        duration_ms = get_audio_duration(voice_path)
    
    # Output in a format that OpenClaw can recognize as voice
    # The Feishu channel should handle this
    print(f"VOICE: {voice_path} | duration={duration_ms}ms")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate and send native voice to Feishu")
    parser.add_argument("--text", required=True, help="Text to convert to speech")
    parser.add_argument("--persona", default="linyan", help="Persona key")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument("--native", action="store_true", help="Output in Feishu native format")
    args = parser.parse_args()
    
    if args.output:
        # Just generate, don't send
        success = generate_voice(args.text, args.persona, args.output)
        print(f"Generated: {args.output}" if success else "Failed")
    elif args.native:
        # Generate and output native format
        out_dir = os.path.expanduser("~/.openclaw/media")
        os.makedirs(out_dir, exist_ok=True)
        mp3_path = os.path.join(out_dir, f"{args.persona}_voice_temp.mp3")
        opus_path = os.path.join(out_dir, f"{args.persona}_voice.opus")
        
        if generate_voice(args.text, args.persona, mp3_path):
            if convert_to_opus(mp3_path, opus_path):
                output_feishu_voice_format(opus_path)
                os.remove(mp3_path)
            else:
                output_feishu_voice_format(mp3_path)
    else:
        # Generate and send
        success = generate_and_send_native_voice(args.text, args.persona, args.chat_id)
        print("Sent successfully" if success else "Failed")
