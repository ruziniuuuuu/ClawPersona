# 语音配置 - 职场御姐型

## TTS 配置
- **引擎**: edge-tts
- **声音**: zh-CN-XiaoyiNeural (成熟知性女声)
- **语速**: 0.95 (略慢，沉稳)
- **音调**: 正常偏低

## 语音特征
- 语调平稳，节奏舒缓
- 停顿得当，给人思考空间
- 音量适中，不疾不徐

## 生成示例
```bash
edge-tts --voice zh-CN-XiaoyiNeural --text "老板，早安。今天的会议资料我已经准备好了，记得吃早餐哦。" --write-media voice_sample.mp3
```
