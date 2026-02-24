#!/usr/bin/env python3
"""
ClawPersona Generate Script Template with Feishu Support
This is a template that can be adapted for all personas
"""
import os
import sys
import base64
import argparse
import urllib.request
from typing import Optional

# Configuration - Override per persona
PERSONA_NAME = "template"
PERSONA_DISPLAY_NAME = "Template"
REF_IMAGE_NAME = "base.jpg"
DEFAULT_PROMPT = "casual photo"

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REF_IMAGE = os.path.join(SKILL_DIR, "assets", REF_IMAGE_NAME)
OUT_DIR = os.path.expanduser("~/.openclaw/media")

def get_api_key() -> str:
    """Get API key from environment or config."""
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        # Try to read from openclaw config
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(config_path):
            import json
            with open(config_path) as f:
                config = json.load(f)
            skill_name = os.path.basename(SKILL_DIR)
            api_key = config.get("skills", {}).get("entries", {}).get(skill_name, {}).get("apiKey")
    return api_key

def generate_image(prompt: str, mode: str = "selfie") -> Optional[str]:
    """Generate image using Doubao API."""
    from openai import OpenAI
    
    api_key = get_api_key()
    if not api_key:
        print("Error: ARK_API_KEY not set", file=sys.stderr)
        return None
    
    if not os.path.exists(REF_IMAGE):
        print(f"Error: Reference image not found: {REF_IMAGE}", file=sys.stderr)
        return None
    
    # Read reference image
    with open(REF_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    # Build prompt based on mode
    mode_templates = {
        "selfie": f"close-up selfie of this person, {prompt}, natural lighting",
        "photo": f"photo of this person, {prompt}, realistic style",
        "mirror": f"mirror selfie of this person, {prompt}, full body visible",
    }
    full_prompt = mode_templates.get(mode, mode_templates["selfie"])
    
    client = OpenAI(
        timeout=300,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    try:
        resp = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=full_prompt,
            size="1920x1920",
            response_format="url",
            extra_body={"image": f"data:image/jpeg;base64,{b64}", "watermark": False}
        )
        
        # Download image
        os.makedirs(OUT_DIR, exist_ok=True)
        out_path = os.path.join(OUT_DIR, f"{PERSONA_NAME}_generated.jpg")
        urllib.request.urlretrieve(resp.data[0].url, out_path)
        
        return out_path
        
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return None

def send_to_platform(image_path: str, platform: str, recipient: Optional[str] = None) -> bool:
    """Send image to specified platform."""
    
    if platform == "imessage":
        import subprocess
        if recipient:
            r = subprocess.run(
                ["imsg", "send", "--to", recipient, "--file", image_path, "--service", "imessage"],
                capture_output=True
            )
            return r.returncode == 0
    
    elif platform == "feishu":
        # Check if running in Feishu environment
        if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
            # Use adapter to handle Feishu output
            sys.path.insert(0, os.path.join(SKILL_DIR, "../../../scripts"))
            try:
                from feishu_adapter import adapt_for_feishu
                result = adapt_for_feishu(image_path)
                print(result)
                return True
            except ImportError:
                pass
        
        # Try webhook if provided
        if recipient and recipient.startswith("http"):
            sys.path.insert(0, os.path.join(SKILL_DIR, "../../../scripts"))
            try:
                from feishu_sender import send_to_feishu
                return send_to_feishu(image_path, webhook_url=recipient)
            except ImportError:
                pass
    
    return False

def main():
    parser = argparse.ArgumentParser(description=f"Generate {PERSONA_DISPLAY_NAME} selfies")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Scene description")
    parser.add_argument("--mode", default="selfie", choices=["selfie", "photo", "mirror"])
    parser.add_argument("--filename", help="Output filename")
    parser.add_argument("--to", help="Recipient (phone for iMessage, URL for Feishu)")
    parser.add_argument("--platform", default="auto", choices=["auto", "imessage", "feishu", "none"])
    args = parser.parse_args()
    
    # Generate image
    image_path = generate_image(args.prompt, args.mode)
    if not image_path:
        sys.exit(1)
    
    # Rename if filename specified
    if args.filename:
        final_path = os.path.join(OUT_DIR, args.filename)
        os.rename(image_path, final_path)
        image_path = final_path
    
    # Determine platform
    platform = args.platform
    if platform == "auto":
        if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
            platform = "feishu"
        elif args.to and (args.to.startswith("+") or args.to.isdigit()):
            platform = "imessage"
        elif args.to and "feishu" in args.to:
            platform = "feishu"
    
    # Send or output
    if platform != "none" and args.to:
        success = send_to_platform(image_path, platform, args.to)
        if not success:
            print(f"MEDIA: {image_path}")
    else:
        # Default output format
        if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
            # In Feishu, try to adapt output
            sys.path.insert(0, os.path.join(SKILL_DIR, "../../../scripts"))
            try:
                from feishu_adapter import adapt_for_feishu
                print(adapt_for_feishu(image_path))
            except ImportError:
                print(f"MEDIA: {image_path}")
        else:
            print(f"MEDIA: {image_path}")

if __name__ == "__main__":
    main()
