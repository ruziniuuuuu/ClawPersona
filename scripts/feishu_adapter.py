#!/usr/bin/env python3
"""
ClawPersona Feishu Adapter
统一处理飞书消息发送
"""
import os
import sys
import json
import urllib.request
import urllib.error
import base64
from typing import Optional, Dict, Any

class FeishuAdapter:
    """适配器：将 MEDIA 输出转换为飞书可发送的格式"""
    
    def __init__(self):
        self.webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")
        self.chat_id = os.environ.get("FEISHU_CHAT_ID")
        
    def process_media_output(self, media_path: str, caption: Optional[str] = None) -> str:
        """
        处理 MEDIA 输出，返回适合飞书的格式
        
        在飞书环境中，我们需要：
        1. 检测是否是飞书环境
        2. 如果是，尝试发送图片
        3. 返回适合飞书的文本格式
        """
        if not self._is_feishu_env():
            # 不是飞书环境，返回原始 MEDIA 格式
            return f"MEDIA: {media_path}"
        
        # 是飞书环境，尝试发送
        if os.path.exists(media_path):
            success = self._send_image_to_feishu(media_path, caption)
            if success:
                return f"[图片已发送到飞书]"
        
        # 发送失败，返回提示
        return f"[图片: {media_path}]"
    
    def _is_feishu_env(self) -> bool:
        """检测当前是否是飞书环境"""
        # 检查是否有飞书相关的环境变量
        return bool(
            os.environ.get("FEISHU_WEBHOOK_URL") or
            os.environ.get("FEISHU_CHAT_ID") or
            os.environ.get("OPENCLAW_CHANNEL") == "feishu"
        )
    
    def _send_image_to_feishu(self, image_path: str, caption: Optional[str] = None) -> bool:
        """发送图片到飞书"""
        if not self.webhook_url:
            return False
        
        try:
            # 读取图片
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # 获取文件扩展名
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
            }.get(ext, "image/jpeg")
            
            # 转换为 base64
            image_base64 = base64.b64encode(image_data).decode()
            
            # 构建消息
            if caption:
                # 图文消息
                payload = {
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": "",
                                "content": [
                                    [
                                        {
                                            "tag": "text",
                                            "text": caption
                                        }
                                    ],
                                    [
                                        {
                                            "tag": "img",
                                            "image_key": self._upload_image(image_data, mime_type) or ""
                                        }
                                    ]
                                ]
                            }
                        }
                    }
                }
            else:
                # 纯图片消息
                image_key = self._upload_image(image_data, mime_type)
                if not image_key:
                    # 上传失败，使用富文本方式
                    payload = {
                        "msg_type": "interactive",
                        "card": {
                            "config": {"wide_screen_mode": True},
                            "elements": [
                                {
                                    "tag": "img",
                                    "title": {"tag": "plain_text", "content": "Selfie"},
                                    "img_key": ""
                                }
                            ]
                        }
                    }
                else:
                    payload = {
                        "msg_type": "image",
                        "content": {
                            "image_key": image_key
                        }
                    }
            
            return self._send_request(payload)
            
        except Exception as e:
            print(f"Error sending image: {e}", file=sys.stderr)
            return False
    
    def _upload_image(self, image_data: bytes, mime_type: str) -> Optional[str]:
        """
        上传图片到飞书获取 image_key
        注意：Webhook 机器人无法直接上传图片，需要 Bot Token
        """
        # Webhook 方式不支持直接上传
        # 需要 Bot App ID 和 Secret 才能调用上传 API
        # 这里返回 None，使用其他方式
        return None
    
    def _send_request(self, payload: Dict[str, Any]) -> bool:
        """发送请求到飞书"""
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
                return result.get("code") == 0
                
        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)
            return False


def adapt_for_feishu(media_path: str, caption: Optional[str] = None) -> str:
    """
    便捷函数：适配 MEDIA 输出到飞书
    
    使用方式：
        output = adapt_for_feishu("/path/to/image.jpg", "看人家的自拍～")
        print(output)
    """
    adapter = FeishuAdapter()
    return adapter.process_media_output(media_path, caption)


if __name__ == "__main__":
    # 测试
    if len(sys.argv) > 1:
        result = adapt_for_feishu(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        print(result)
    else:
        print("Usage: python3 feishu_adapter.py <image_path> [caption]")
