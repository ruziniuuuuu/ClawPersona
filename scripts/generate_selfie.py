#!/usr/bin/env python3
"""
ClawPersona Selfie Generator with Native Feishu Support
Generates persona selfies and sends them directly to Feishu when in Feishu environment
"""
import os
import base64
import argparse
import urllib.request
import sys
from typing import Optional

# Try to import OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not found. Install with: pip install openai")
    sys.exit(1)

# Default output directory
OUT_DIR = os.path.expanduser("~/.openclaw/media")


def get_ref_image_path() -> str:
    """Get reference image path from script location"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/base.jpg")


def get_modes(persona: str) -> dict:
    """Get prompt modes for persona"""
    # Default modes - can be overridden per persona
    return {
        "mirror": f"photo of this person taking a mirror selfie, {{prompt}}, realistic photography",
        "selfie": f"close-up selfie of this person, {{prompt}}, realistic photography",
        "photo": f"photo of this person, {{prompt}}, realistic photography",
    }


def generate_selfie(prompt: str, ref_image_path: str, output_path: str, api_key: Optional[str] = None) -> bool:
    """
    Generate selfie using Doubao Seedream API
    
    Args:
        prompt: The prompt for image generation
        ref_image_path: Path to reference image
        output_path: Output path for generated image
        api_key: Doubao API key (optional, defaults to ARK_API_KEY env var)
    
    Returns:
        True if successful
    """
    if not os.path.exists(ref_image_path):
        print(f"Error: Reference image not found: {ref_image_path}", file=sys.stderr)
        return False
    
    api_key = api_key or os.environ.get("ARK_API_KEY")
    if not api_key:
        print("Error: ARK_API_KEY not set", file=sys.stderr)
        return False
    
    try:
        with open(ref_image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        
        client = OpenAI(
            timeout=300,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="1920x1920",
            response_format="url",
            extra_body={"image": f"data:image/jpeg;base64,{b64}", "watermark": False}
        )
        
        urllib.request.urlretrieve(resp.data[0].url, output_path)
        return True
        
    except Exception as e:
        print(f"Error generating selfie: {e}", file=sys.stderr)
        return False


def send_to_feishu_native(media_path: str, caption: Optional[str] = None) -> bool:
    """
    Send media to Feishu using native integration
    
    Args:
        media_path: Path to media file
        caption: Optional caption
    
    Returns:
        True if sent successfully
    """
    try:
        # Import feishu_native module
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(script_dir, "../../../workspace/ClawPersona/scripts"))
        
        from feishu_native import is_feishu_env, send_media_to_feishu
        
        if is_feishu_env():
            return send_media_to_feishu(media_path, caption=caption)
        return False
        
    except Exception as e:
        print(f"Warning: Feishu native send failed: {e}", file=sys.stderr)
        return False


def handle_output(media_path: str, to: Optional[str] = None, caption: Optional[str] = None) -> str:
    """
    Handle output - send to appropriate channel or output MEDIA format
    
    Args:
        media_path: Path to media file
        to: Target channel (e.g., "+1234567890" for iMessage, "feishu:xxx" for Feishu)
        caption: Optional caption
    
    Returns:
        Output string
    """
    # Try Feishu native first
    if send_to_feishu_native(media_path, caption):
        return "[已发送到飞书]"
    
    # Handle explicit targets
    if to:
        if to.startswith("+") or to.isdigit():
            # iMessage
            try:
                import subprocess
                r = subprocess.run(["imsg", "send", "--to", to, "--file", media_path, "--service", "imessage"], 
                                 capture_output=True)
                if r.returncode == 0:
                    return f"sent: {media_path}"
            except:
                pass
        elif to.startswith("feishu:"):
            # Feishu webhook (legacy)
            pass
    
    # Default: output MEDIA format
    return f"MEDIA: {media_path}"


def main():
    parser = argparse.ArgumentParser(description="Generate ClawPersona selfie with Feishu native support")
    parser.add_argument("--prompt", required=True, help="Prompt for image generation")
    parser.add_argument("--mode", default="photo", choices=["mirror", "selfie", "photo"], 
                       help="Generation mode")
    parser.add_argument("--filename", default="selfie.jpg", help="Output filename")
    parser.add_argument("--to", default=None, help="Target (phone number for iMessage, etc.)")
    parser.add_argument("--caption", help="Caption for the image")
    parser.add_argument("--persona", default="default", help="Persona key for mode selection")
    args = parser.parse_args()
    
    # Setup paths
    ref_image = get_ref_image_path()
    os.makedirs(OUT_DIR, exist_ok=True)
    output_path = os.path.join(OUT_DIR, args.filename)
    
    # Get prompt modes
    modes = get_modes(args.persona)
    prompt = modes[args.mode].format(prompt=args.prompt)
    
    # Generate selfie
    if not generate_selfie(prompt, ref_image, output_path):
        sys.exit(1)
    
    # Handle output
    result = handle_output(output_path, args.to, args.caption)
    print(result)


if __name__ == "__main__":
    main()
