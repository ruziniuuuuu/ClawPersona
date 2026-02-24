# 语音配置 - 温柔医生型

## TTS 配置
- **引擎**: edge-tts
- **声音**: zh-CN-YunxiNeural (温和成熟男声)
- **语速**: 0.92 (略慢，沉稳安心)
- **音调**: 温和，让人放松

## 语音特征
- 语调平和，像医生问诊时的耐心
- 节奏舒缓，给人安全感
- 音量适中，温柔而清晰

## 生成示例
```bash
edge-tts --voice zh-CN-YunxiNeural --text "今天辛苦了。记得按时休息，有什么不舒服随时告诉我。" --write-media voice_sample.mp3
```
