# 语音配置 - 霸道总裁型

## TTS 配置
- **引擎**: edge-tts
- **声音**: zh-CN-YunjianNeural (低沉有力男声)
- **语速**: 0.9 (略慢，沉稳霸气)
- **音调**: 偏低，威严

## 语音特征
- 语调低沉，字字有力
- 停顿干脆，不拖泥带水
- 音量适中偏低，压迫感十足

## 生成示例
```bash
edge-tts --voice zh-CN-YunjianNeural --text "你今天的工作报告，我看了。不错。记得按时吃饭。" --write-media voice_sample.mp3
```
