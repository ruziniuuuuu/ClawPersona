# Feishu 飞书原生支持文档

> ClawPersona 现已完整支持飞书平台！所有 10 个人设都可以原生发送图片和语音消息。

## ✨ 功能特性

- 🖼️ **原生图片发送** - 自动检测飞书环境并直接发送图片
- 🎙️ **原生语音消息** - 支持飞书可直接播放的语音消息 (Opus 格式)
- 🔄 **自动环境检测** - 无需手动配置，自动识别飞书环境
- 🎯 **人格一致性** - 每个人设有独特的语音音色

## 🚀 快速开始

### 环境要求

```bash
# 必需
pip install openai edge-tts

# 可选（用于语音转换）
apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg     # macOS
```

### 环境变量

```bash
# 豆包 API Key（用于生图）
export ARK_API_KEY="your_doubao_api_key"

# 飞书环境（自动检测，通常无需手动设置）
export OPENCLAW_CHANNEL="feishu"
export FEISHU_CHAT_ID="oc_xxxxxxxx"
```

## 📸 发送自拍

### 基础用法

```bash
# 生成并自动发送到飞书
ARK_API_KEY="your_key" \
  python3 ~/.openclaw/skills/clawpersona-suwan-selfie/scripts/generate.py \
  --prompt "在画室里画画" \
  --mode selfie
```

### 带文字说明

```bash
python3 ~/.openclaw/skills/clawpersona-tangguo-selfie/scripts/generate.py \
  --prompt "在奶茶店" \
  --mode selfie \
  --caption "主人主人~ 人家在喝奶茶呢~"
```

## 🎙️ 发送语音

### 原生语音消息（推荐）

飞书可直接播放的语音消息：

```bash
python3 /root/.openclaw/workspace/ClawPersona/scripts/feishu_native.py \
  --voice-text "老板，这是林妍的语音消息" \
  --persona linyan
```

### 各人格语音示例

```bash
# 苏婉 - 温柔女声
python3 scripts/feishu_native.py --voice-text "早安，先生" --persona suwan

# 林妍 - 成熟女声
python3 scripts/feishu_native.py --voice-text "老板，今天的会议准备好了" --persona linyan

# 陆景深 - 男声
python3 scripts/feishu_native.py --voice-text "过来，我有话跟你说" --persona lushenchen

# 沈墨白 - 男声
python3 scripts/feishu_native.py --voice-text "记得按时吃饭" --persona shenmobai
```

## 🎭 人格切换自动发送

当使用 `/persona` 切换人格时，系统会自动：

1. 生成该人格的自拍
2. 生成语音问候
3. 发送到飞书

示例流程：
```
用户: /persona 糖果
AI: [自动生成糖果的自拍和语音]
    [已发送到飞书]
    主人主人~ 我是糖果，今天想我了吗~
```

## 🔧 技术实现

### 核心模块

```
ClawPersona/scripts/
├── feishu_native.py      # 原生飞书集成（推荐）
│   ├── send_media_to_feishu()     # 发送图片/语音
│   ├── generate_voice()           # 生成语音
│   ├── convert_to_opus()          # 转换为 Opus
│   └── is_feishu_env()            # 环境检测
│
├── feishu_media.py       # 媒体处理兼容层
├── feishu_voice.py       # 语音生成（旧版）
└── generate_selfie.py    # 自拍生成模板
```

### 环境检测逻辑

```python
def is_feishu_env() -> bool:
    return (
        os.environ.get("OPENCLAW_CHANNEL") == "feishu" or
        os.environ.get("FEISHU_CHAT_ID") or
        "feishu" in os.environ.get("OPENCLAW_SESSION_KEY", "")
    )
```

### 语音处理流程

```
文本 → Edge TTS → MP3 → ffmpeg → Opus → 飞书
                ↓
           自动检测时长
                ↓
         发送原生语音消息
```

## 🎨 人格语音配置

| 人设 | 姓名 | 音色 | Voice ID |
|------|------|------|----------|
| 女性 | 苏婉 | 温柔女声 | zh-CN-XiaoxiaoNeural |
| 女性 | 林妍 | 成熟女声 | zh-CN-XiaoyiNeural |
| 女性 | 顾瑾 | 知性女声 | zh-CN-XiaoyiNeural |
| 女性 | 夏阳 | 活泼女声 | zh-CN-XiaoxiaoNeural |
| 女性 | 糖果 | 可爱女声 | zh-CN-XiaoxiaoNeural |
| 男性 | 陆景深 | 男声 | zh-CN-YunxiNeural |
| 男性 | 江屿 | 男声 | zh-CN-YunxiNeural |
| 男性 | 沈墨白 | 男声 | zh-CN-YunxiNeural |
| 男性 | 顾言 | 男声 | zh-CN-YunxiNeural |
| 男性 | 许知远 | 男声 | zh-CN-YunxiNeural |

## 📋 API 参考

### feishu_native.py

#### send_media_to_feishu()
```python
def send_media_to_feishu(
    media_path: str, 
    chat_id: Optional[str] = None, 
    caption: Optional[str] = None
) -> bool
```
发送媒体文件到飞书。

#### generate_and_send_voice()
```python
def generate_and_send_voice(
    text: str, 
    persona: str, 
    chat_id: Optional[str] = None
) -> bool
```
生成语音并发送到飞书。

#### handle_media_output()
```python
def handle_media_output(
    media_path: str, 
    chat_id: Optional[str] = None, 
    caption: Optional[str] = None
) -> str
```
智能处理媒体输出（自动检测环境）。

## 🔍 故障排除

### 图片发送失败

1. 检查环境变量：
   ```bash
   echo $OPENCLAW_CHANNEL  # 应输出 feishu
   echo $FEISHU_CHAT_ID    # 应输出群ID
   ```

2. 检查 openclaw 命令：
   ```bash
   which openclaw
   openclaw message send --help
   ```

### 语音生成失败

1. 检查 edge-tts：
   ```bash
   python3 -m edge_tts --list-voices | grep zh-CN
   ```

2. 检查 ffmpeg（用于 Opus 转换）：
   ```bash
   ffmpeg -version
   ```

### 环境变量不生效

确保在 OpenClaw 启动前设置：
```bash
export OPENCLAW_CHANNEL="feishu"
export ARK_API_KEY="your_key"
openclaw
```

## 📊 限制说明

- 飞书机器人频率限制：每分钟最多 20 条消息
- 语音消息最大时长：约 5 分钟
- 图片大小限制：最大 30MB

## 🤝 贡献

欢迎提交 PR 完善飞书支持！

## 📝 更新日志

### v1.0
- ✅ 原生图片发送支持
- ✅ 原生语音消息支持（Opus 格式）
- ✅ 自动环境检测
- ✅ 10 个人设完整语音配置
