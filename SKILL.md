---
name: doubao-image-reader
description: >
  豆包 AI 图片理解 — 通过本地逆向 API（doubao-free-api）读取并理解图片内容。
  支持多模态图片识别、文字提取、语义分析。仅用于图片读取，不用于生图。
---

# 豆包 AI 图片理解（多模态读图）

## 方案概述

通过本地部署的 doubao-free-api 逆向服务，将豆包的图片理解能力封装为 OpenAI 兼容 API。

```
用户图片 → base64 编码 → 本地代理 (localhost:8000) → 豆包多模态 → 文本描述
```

**定位：** 仅用于图片读取和识别（多模态理解），不用于图片生成。可作为 DeepSeek V4 等模型的图片理解补充方案。

## 环境依赖

- 本地部署 doubao-free-api 服务（PM2 保活）
- 服务端口：`localhost:8000`
- Session ID：从 doubao.com 浏览器 Cookie 获取

## 环境变量

```bash
# 在 .env 中配置
DOUBAO_SESSION_ID=你的sessionid
```

## 调用方式

### 读图（多模态）

**端点：** `POST http://localhost:8000/v1/chat/completions`

**请求体：**
```json
{
  "model": "doubao",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ],
  "stream": false
}
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| model | 是 | 固定 `"doubao"` |
| messages[0].content | 是 | 混合文本+图片内容数组 |
| content[].type | 是 | `"text"` 或 `"image_url"` |
| image_url.url | 是 | 图片URL或data:image base64 |
| stream | 否 | 关闭流式（固定 false） |

### 图片传入方式

**推荐 base64（最稳定）：**
```python
import base64
with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
url = f"data:image/png;base64,{b64}"
```

**URL 方式（图片需可公开访问）：**
```json
{"type": "image_url", "image_url": {"url": "https://example.com/photo.jpg"}}
```

> ⚠️ 部分网站可能 403，推荐使用 base64。
> ⚠️ 大图建议缩放到 800px 后再传 base64 以节省带宽。

## 部署说明

### 1. 安装服务

```bash
# 克隆项目
git clone https://github.com/Bitsea1/doubao-free-api.git /tmp/doubao-free-api
cd /tmp/doubao-free-api

# 安装依赖
npm install

# 构建
npm run build

# 使用 PM2 保活
pm2 start npm --name doubao-free-api -- start
pm2 save
```

### 2. 获取 Session ID

1. 浏览器打开 https://www.doubao.com
2. 登录账号
3. F12 → Application → Cookies → 复制 sessionid
4. 配置到 .env 文件：`DOUBAO_SESSION_ID=你的sessionid`

### 3. 验证服务

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 基本用法

### 示例 1：读取本地图片

```python
import requests
import base64
import json

def read_image(image_path, prompt="详细描述这张图片"):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": "doubao",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{b64}"
                }}
            ]
        }],
        "stream": False
    }
    
    resp = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json=payload,
        timeout=60
    )
    return resp.json()["choices"][0]["message"]["content"]
```

### 示例 2：识别图片中的文字

```python
text = read_image("receipt.jpg", "提取这张图片中的所有文字")
```

### 示例 3：对比分析多张图片

```python
# 逐张调用，对比结果
descriptions = []
for img in ["photo1.jpg", "photo2.jpg"]:
    desc = read_image(img, "描述这张图片")
    descriptions.append(desc)

# 对比分析
comparison = requests.post(...)  # 将描述传给聊天模型做对比
```

## 注意事项

- ⚠️ **仅限学习使用，不作商用**，存在被封禁风险
- ⚠️ **Session ID 会过期**，需定期从 doubao.com 重新获取
- 图片 URL 优先用 base64 方式（部分网站可能被 403）
- 大图建议缩放到 800px 再传 base64
- 不支持视频输入
- 图片理解能力建议通过实际测试与 DeepSeek V4 等模型对比评估

## 与 DeepSeek V4 图片理解对比

| 维度 | 豆包 | DeepSeek V4 |
|------|------|-------------|
| 部署方式 | 本地服务 | 云端 API |
| 图片上传 | base64/URL | URL 或附件 |
| 多轮对话 | 支持 | 支持 |
| 稳定性 | 需保持 Session 有效 | 官方稳定 |
| 延迟 | 较快（本地代理） | 取决于网络 |
| 成本 | 免费 | 按量付费 |
| 建议场景 | 本地自动化、批量读图 | 少量偶发读图 |
