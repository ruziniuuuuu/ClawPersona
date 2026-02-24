#!/usr/bin/env python3
"""
Send native voice message to Feishu using direct API call
"""
import os
import sys
import json
import subprocess
from typing import Optional

def get_feishu_credentials() -> tuple:
    """Get Feishu app ID and secret from config"""
    try:
        # Read OpenClaw JSON config
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            
            # Try to get Feishu credentials
            feishu_config = config.get("channels", {}).get("feishu", {})
            if isinstance(feishu_config, dict):
                return feishu_config.get("appId"), feishu_config.get("appSecret")
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
    
    # Try environment variables
    return os.environ.get("FEISHU_APP_ID"), os.environ.get("FEISHU_APP_SECRET")


def get_tenant_access_token(app_id: str, app_secret: str) -> Optional[str]:
    """Get tenant access token from Feishu"""
    import urllib.request
    import urllib.error
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("code") == 0:
                return result.get("tenant_access_token")
            else:
                print(f"Token error: {result}", file=sys.stderr)
    except Exception as e:
        print(f"Token request failed: {e}", file=sys.stderr)
    
    return None


def upload_audio_file(token: str, file_path: str, duration_ms: int) -> Optional[str]:
    """Upload audio file to Feishu and get file_key"""
    import urllib.request
    import urllib.error
    import mimetypes
    
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    
    file_name = os.path.basename(file_path)
    file_type = "opus"  # For voice messages, use opus
    
    # Guess content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "audio/opus"
    
    # Build multipart form data manually
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # Build body parts
    lines = []
    
    # file_type field
    lines.append(f"--{boundary}")
    lines.append('Content-Disposition: form-data; name="file_type"')
    lines.append("")
    lines.append(file_type)
    
    # duration field (required for audio)
    lines.append(f"--{boundary}")
    lines.append('Content-Disposition: form-data; name="duration"')
    lines.append("")
    lines.append(str(duration_ms))
    
    # file field
    lines.append(f"--{boundary}")
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{file_name}"')
    lines.append(f"Content-Type: {content_type}")
    lines.append("")
    
    # Convert to bytes
    body_lines = "\r\n".join(lines).encode("utf-8")
    body_end = f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    data = body_lines + b"\r\n" + file_data + b"\r\n" + body_end
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            print(f"Upload response: {result}", file=sys.stderr)
            if result.get("code") == 0:
                return result.get("data", {}).get("file_key")
            else:
                print(f"Upload error: {result}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Upload HTTP error {e.code}: {error_body}", file=sys.stderr)
    except Exception as e:
        print(f"Upload failed: {e}", file=sys.stderr)
    
    return None


def send_audio_message(token: str, chat_id: str, file_key: str, duration_ms: int) -> bool:
    """Send audio message to Feishu"""
    import urllib.request
    import urllib.error
    
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    content = json.dumps({
        "file_key": file_key,
        "duration": duration_ms
    })
    
    data = json.dumps({
        "receive_id": chat_id,
        "msg_type": "audio",
        "content": content
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("code") == 0:
                print("Audio message sent successfully")
                return True
            else:
                print(f"Send error: {result}", file=sys.stderr)
    except Exception as e:
        print(f"Send failed: {e}", file=sys.stderr)
    
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
    
    # Estimate
    file_size = os.path.getsize(file_path)
    return int((file_size * 8 / 24000) * 1000)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Send native voice to Feishu")
    parser.add_argument("voice_file", help="Path to voice file (opus)")
    parser.add_argument("--chat-id", help="Feishu chat ID")
    parser.add_argument("--duration", type=int, help="Duration in milliseconds")
    args = parser.parse_args()
    
    if not os.path.exists(args.voice_file):
        print(f"Error: File not found: {args.voice_file}", file=sys.stderr)
        sys.exit(1)
    
    # Get credentials
    app_id, app_secret = get_feishu_credentials()
    if not app_id or not app_secret:
        print("Error: Feishu credentials not found", file=sys.stderr)
        sys.exit(1)
    
    # Get token
    token = get_tenant_access_token(app_id, app_secret)
    if not token:
        print("Error: Failed to get access token", file=sys.stderr)
        sys.exit(1)
    
    # Get chat ID
    chat_id = args.chat_id or os.environ.get("FEISHU_CHAT_ID")
    if not chat_id:
        print("Error: Chat ID not found", file=sys.stderr)
        sys.exit(1)
    
    # Get duration
    duration = args.duration or get_audio_duration(args.voice_file)
    
    # Upload file
    file_key = upload_audio_file(token, args.voice_file, duration)
    if not file_key:
        print("Error: Failed to upload file", file=sys.stderr)
        sys.exit(1)
    
    # Send message
    success = send_audio_message(token, chat_id, file_key, duration)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
