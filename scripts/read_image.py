#!/usr/bin/env python3
"""
豆包读图脚本 — 多模态图片理解
用法：
  python3 read_image.py <图片路径> [提示词]
  python3 read_image.py <图片URL> [提示词]
"""
import sys
import os
import base64
import requests
import json

DOUBAO_API = "http://localhost:8000/v1/chat/completions"

def read_image(image_source, prompt="详细描述这张图片"):
    """读取本地图片或URL图片"""
    
    if image_source.startswith(("http://", "https://")):
        # URL 方式
        image_content = {"type": "image_url", "image_url": {"url": image_source}}
    else:
        # 本地文件 → base64
        with open(image_source, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(image_source)[1].lower().replace(".", "")
        if ext in ("jpg", "jpeg"):
            mime = "image/jpeg"
        elif ext == "png":
            mime = "image/png"
        elif ext == "webp":
            mime = "image/webp"
        elif ext == "gif":
            mime = "image/gif"
        else:
            mime = "image/png"
        image_content = {"type": "image_url", "image_url": {
            "url": f"data:{mime};base64,{b64}"
        }}
    
    payload = {
        "model": "doubao",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                image_content
            ]
        }],
        "stream": False
    }
    
    resp = requests.post(DOUBAO_API, json=payload, timeout=120)
    if resp.status_code != 200:
        print(f"错误: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    
    result = resp.json()
    content = result["choices"][0]["message"]["content"]
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 read_image.py <图片路径/URL> [提示词]")
        sys.exit(1)
    
    image = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "详细描述这张图片"
    
    result = read_image(image, prompt)
    print(result)
