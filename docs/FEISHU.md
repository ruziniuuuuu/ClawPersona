# Feishu 飞书支持文档

## 概述

ClawPersona 现已支持飞书平台！所有 10 个人设都可以生成自拍并通过飞书发送。

## 快速开始

### 1. 配置飞书 Webhook

设置环境变量：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
export OPENCLAW_CHANNEL="feishu"  # 让 skill 自动检测飞书环境
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
└── generate_template.py  # 带飞书支持的模板
```

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `FEISHU_WEBHOOK_URL` | 飞书机器人的 webhook 地址 | 是（用于发送） |
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

1. 检查 webhook URL 是否正确
2. 检查机器人是否有发送图片权限
3. 查看错误日志：`python3 scripts/feishu_sender.py --image test.jpg --webhook URL`

### 环境变量不生效

确保在启动 OpenClaw 前设置：
```bash
export OPENCLAW_CHANNEL="feishu"
export FEISHU_WEBHOOK_URL="https://..."
```

### 飞书 webhook 限制

飞书 webhook 有频率限制：
- 每个机器人每分钟最多发送 20 条消息
- 图片需要通过上传获取 image_key

## 待完善功能

- [ ] 支持飞书 Bot Token 方式（支持更多 API）
- [ ] 支持图片上传获取 image_key
- [ ] 支持富文本卡片消息
- [ ] 支持语音消息发送

## 贡献

欢迎提交 PR 完善飞书支持！
