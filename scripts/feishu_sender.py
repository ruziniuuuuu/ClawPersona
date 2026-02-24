#!/usr/bin/env python3
"""Feishu message sender for ClawPersona."""
import os
import json
import urllib.request
import urllib.error
from typing import Optional

class FeishuSender:
    """Send messages and media to Feishu."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize with webhook URL or read from env."""
        self.webhook_url = webhook_url or os.environ.get("FEISHU_WEBHOOK_URL")
        self.app_id = os.environ.get("FEISHU_APP_ID")
        self.app_secret = os.environ.get("FEISHU_APP_SECRET")
        
    def send_text(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Send text message to Feishu."""
        if not self.webhook_url:
            print("Error: FEISHU_WEBHOOK_URL not set")
            return False
            
        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        
        return self._send_payload(payload)
    
    def send_image(self, image_path: str, chat_id: Optional[str] = None) -> bool:
        """Send image to Feishu."""
        if not os.path.exists(image_path):
            print(f"Error: Image not found: {image_path}")
            return False
            
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        import base64
        image_base64 = base64.b64encode(image_data).decode()
        
        # For webhook bot, we need to upload image first or use image_key
        # For now, we'll use a simpler approach with interactive cards
        payload = {
            "msg_type": "image",
            "content": {
                "image_key": self._upload_image(image_path) or ""
            }
        }
        
        return self._send_payload(payload)
    
    def send_image_card(self, image_path: str, text: Optional[str] = None) -> bool:
        """Send image as a card message (more reliable)."""
        if not os.path.exists(image_path):
            print(f"Error: Image not found: {image_path}")
            return False
        
        # For webhook, we can use the image_key approach
        # But first we need to upload the image to get a key
        image_key = self._upload_image(image_path)
        
        if not image_key:
            # Fallback: use interactive card with image URL
            # This requires the image to be accessible via URL
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                            "tag": "img",
                            "img_key": image_key or "",
                            "alt": {
                                "tag": "plain_text",
                                "content": "Selfie"
                            }
                        }
                    ]
                }
            }
            if text:
                payload["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": text
                    }
                })
        else:
            payload = {
                "msg_type": "image",
                "content": {
                    "image_key": image_key
                }
            }
            
        return self._send_payload(payload)
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """Upload image to Feishu and get image_key."""
        # This requires bot token, not webhook
        # For webhook bots, images need to be uploaded via Feishu API
        # For now, return None and use alternative methods
        return None
    
    def _send_payload(self, payload: dict) -> bool:
        """Send payload to Feishu webhook."""
        if not self.webhook_url:
            print("Error: FEISHU_WEBHOOK_URL not set")
            return False
            
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                if result.get("code") == 0:
                    print(f"sent: {payload.get('msg_type', 'message')}")
                    return True
                else:
                    print(f"Error: {result}")
                    return False
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.read().decode()}")
            return False
        except Exception as e:
            print(f"Error sending to Feishu: {e}")
            return False


def send_to_feishu(image_path: str, text: Optional[str] = None, 
                   webhook_url: Optional[str] = None) -> bool:
    """Convenience function to send image to Feishu."""
    sender = FeishuSender(webhook_url)
    
    # First try to send image
    if image_path and os.path.exists(image_path):
        success = sender.send_image_card(image_path, text)
        if success:
            return True
    
    # Fallback: just send text with MEDIA path
    if text:
        sender.send_text(text)
    
    print(f"MEDIA: {image_path}")
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send media to Feishu")
    parser.add_argument("--image", help="Image path to send")
    parser.add_argument("--text", help="Text message")
    parser.add_argument("--webhook", help="Feishu webhook URL")
    args = parser.parse_args()
    
    send_to_feishu(args.image, args.text, args.webhook)
