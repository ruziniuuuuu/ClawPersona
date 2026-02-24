# Feishu 飞书支持文档

## 概述

ClawPersona 现已支持飞书平台！所有 10 个人设都可以生成自拍并通过飞书发送。

## 快速开始

### 1. 配置飞书环境

设置环境变量：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
export OPENCLAW_CHANNEL="feishu"  # 让 skill 自动检测飞书环境
export FEISHU_CHAT_ID="oc_xxxxxxxx"  # 飞书聊天群ID
```

### 2. 生成并发送自拍

#### 方式一：命令行直接发送
```bash
# 使用 feishu: 前缀指定 webhook
ARK_API_KEY="your_key" \
  python3 /root/.openclaw/skills/clawpersona-tangguo-selfie/scripts/generate.py \
  --prompt "at a trendy bubble tea shop" \
  --mode selfie \
  --to "feishu:$FEISHU_WEBHOOK_URL"
```

#### 方式二：使用独立发送脚本
```bash
# 先生成图片
ARK_API_KEY="your_key" \
  python3 /root/.openclaw/skills/clawpersona-tangguo-selfie/scripts/generate.py \
  --prompt "wearing cute outfit" \
  --mode selfie \
  --filename my_selfie.jpg

# 再发送到飞书
python3 /root/.openclaw/workspace/ClawPersona/scripts/feishu_sender.py \
  --image /root/.openclaw/media/my_selfie.jpg \
  --text "主人主人～看人家的新自拍！" \
  --webhook "$FEISHU_WEBHOOK_URL"
```

### 3. 发送语音消息

#### 发送原生语音（推荐）
```bash
# 生成并发送原生语音消息（飞书可直接播放）
python3 /root/.openclaw/workspace/ClawPersona/scripts/feishu_voice.py \
  --text "老板，这是林妍的语音消息" \
  --persona linyan \
  --chat-id "$FEISHU_CHAT_ID"
```

#### 发送为媒体文件
```bash
# 以文件形式发送（需要点击下载）
python3 /root/.openclaw/workspace/ClawPersona/scripts/feishu_voice.py \
  --text "老板，这是语音文件" \
  --persona linyan \
  --chat-id "$FEISHU_CHAT_ID" \
  --media
```

#### 只生成语音
```bash
python3 /root/.openclaw/workspace/ClawPersona/scripts/feishu_voice.py \
  --text "早安，先生" \
  --persona suwan \
  --output /root/.openclaw/media/suwan_voice.opus
```

#### 支持的音色
| 人设 | 音色 | Voice ID |
|------|------|----------|
| 苏婉、夏阳、糖果 | 温柔女声 | zh-CN-XiaoxiaoNeural |
| 林妍、顾瑾 | 成熟女声 | zh-CN-XiaoyiNeural |
| 陆景深、江屿、沈墨白、顾言、许知远 | 男声 | zh-CN-YunxiNeural |

### 3. 在 OpenClaw 中使用

当 `OPENCLAW_CHANNEL=feishu` 时，skill 会自动适配输出格式：
```bash
# 设置环境变量后运行 OpenClaw
export OPENCLAW_CHANNEL="feishu"
export FEISHU_WEBHOOK_URL="https://..."
openclaw
```

然后在对话中：
```
用户: 发张自拍
AI: [自动生成并发送到飞书]
```

## 人格切换时的自动发送

当使用 `/persona` 切换人格时，会自动生成自拍和语音：

```bash
/persona 糖果
```

这会触发：
1. 生成糖果的自拍
2. 生成语音问候（需要 edge-tts）
3. 发送到飞书（如果配置了 webhook）

## 技术细节

### 文件结构
```
ClawPersona/scripts/
├── feishu_sender.py      # 飞书消息发送器
├── feishu_adapter.py     # 输出格式适配器
├── feishu_direct.py      # 直接发送图片到飞书
├── feishu_voice.py       # 生成并发送语音
└── generate_template.py  # 带飞书支持的模板
```

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `FEISHU_WEBHOOK_URL` | 飞书机器人的 webhook 地址 | 否（用于 webhook 发送） |
| `FEISHU_CHAT_ID` | 飞书聊天群ID | 是（用于直接发送） |
| `OPENCLAW_CHANNEL` | 当前渠道，设为 `feishu` 自动适配 | 否（推荐设置） |
| `ARK_API_KEY` | 豆包 API Key | 是（用于生图） |

### 发送流程

```
生成图片
    ↓
检测 OPENCLAW_CHANNEL
    ↓
如果是 feishu:
    - 尝试使用 feishu_adapter 适配输出
    - 或直接调用 feishu_sender 发送
否则:
    - 输出 MEDIA: path 格式
```

## 故障排除

### 图片发送失败

1. 检查 `FEISHU_CHAT_ID` 是否正确设置
2. 检查机器人是否有发送图片权限
3. 查看错误日志：`python3 scripts/feishu_direct.py --image test.jpg`

### 语音发送失败

1. 确保已安装 edge-tts：`pip install edge-tts`
2. 检查网络连接（Edge TTS 需要访问微软服务）
3. 查看支持的音色：`python3 -m edge_tts --list-voices | grep zh-CN`

### 环境变量不生效

确保在启动 OpenClaw 前设置：
```bash
export OPENCLAW_CHANNEL="feishu"
export FEISHU_CHAT_ID="oc_xxxxxxxx"
```

### 飞书频率限制

飞书对消息发送有限制：
- 每个机器人每分钟最多发送 20 条消息
- 图片和语音都通过文件上传方式发送

## 待完善功能

- [x] 支持飞书图片直接发送
- [x] 支持原生语音消息发送（可直接播放）
- [ ] 支持飞书 Bot Token 方式（支持更多 API）
- [ ] 支持图片上传获取 image_key
- [ ] 支持富文本卡片消息
- [ ] 支持人格切换时自动发送语音问候

## 贡献

欢迎提交 PR 完善飞书支持！
