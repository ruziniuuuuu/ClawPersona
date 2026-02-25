# Feishu 飞书支持

ClawPersona 支持飞书原生图片和语音输出。

## 快速开始

### 1. 环境要求

```bash
pip install openai edge-tts
```

### 2. 环境变量

```bash
export ARK_API_KEY="your_doubao_key"
```

## 使用

### 发送自拍

```bash
# 生成并自动发送到飞书
ARK_API_KEY="your_key" \
  python3 ~/.openclaw/skills/clawpersona-suwan-selfie/scripts/generate.py \
  --prompt "在画室里画画" --mode selfie
```

### 发送语音

```bash
python3 scripts/feishu.py --voice "早安，先生" --persona suwan
```

## 人格语音

| 人设 | Voice ID |
|------|----------|
| 苏婉、夏阳、糖果 | zh-CN-XiaoxiaoNeural |
| 林妍、顾瑾 | zh-CN-XiaoyiNeural |
| 陆景深、江屿、沈墨白、顾言、许知远 | zh-CN-YunxiNeural |
