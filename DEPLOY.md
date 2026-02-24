# ClawPersona 部署指南

## 环境要求

- **macOS** (推荐) 或 Linux
- **Node.js** v18+
- **Python** 3.10+
- **uv** (Python 包管理器)
- **OpenClaw** 最新版本

## 1. 安装依赖

```bash
brew install node python uv
npm install -g openclaw
```

验证：

```bash
node --version    # v18+
python3 --version # 3.10+
uv --version
openclaw --version
```

## 2. 获取豆包 API Key

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通「方舟」服务，创建 API Key
3. 开通 `doubao-seedream-4-5-251128` 模型权限

## 3. 安装 ClawPersona

```bash
git clone https://github.com/TATP-233/ClawPersona.git ~/ws/ClawPersona
cd ~/ws/ClawPersona
npm install -g .
```

然后运行安装向导：

```bash
npx clawpersona@latest
```

向导会引导你：
1. 输入豆包 API Key
2. 选择要安装的人格
3. 设置默认人格

**或者手动安装所有 10 个人格：**

```bash
node -e "
const { installSkills, ensureDirectories } = require('./src/installer');
ensureDirectories();
installSkills(
  ['suwan','linyan','gujin','xiayang','tangguo','lushenchen','jiangyu','shenmobai','guyan','xuzhiyuan'],
  'your_ark_api_key_here'
);
console.log('done');
"
```

## 4. 验证安装

检查 skill 是否已安装：

```bash
ls ~/.openclaw/skills/ | grep clawpersona
```

应看到 10 个目录：

```
clawpersona-gujin-selfie
clawpersona-guyan-selfie
clawpersona-jiangyu-selfie
clawpersona-linyan-selfie
clawpersona-lushenchen-selfie
clawpersona-shenmobai-selfie
clawpersona-suwan-selfie
clawpersona-tangguo-selfie
clawpersona-xiayang-selfie
clawpersona-xuzhiyuan-selfie
```

检查 openclaw.json 配置（每个 skill 应有 `apiKey` 字段）：

```bash
python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.openclaw/openclaw.json')))
for k, v in d['skills']['entries'].items():
    if 'clawpersona' in k:
        print(k, '- apiKey:', 'OK' if v.get('apiKey') else 'MISSING')
"
```

## 5. 重启 OpenClaw

```bash
pkill -f openclaw-gateway; sleep 1; openclaw &
```

## 6. 测试人格切换

```bash
node ~/ws/ClawPersona/commands/persona 苏婉
```

正常输出：

```
MEDIA: /Users/<you>/.openclaw/workspace/greeting.mp3
MEDIA: /Users/<you>/.openclaw/workspace/greeting.jpg
已切换到苏婉模式 🎨 你好呀，我是苏婉，一个喜欢画画的插画师～
```

在 OpenClaw 对话中使用：

```
/persona 苏婉
/persona 陆景深
/persona-list
```

## 7. 故障排除

**图片生成失败 / API 401**
- 检查 `~/.openclaw/openclaw.json` 里 skill 的 `apiKey` 字段是否正确
- 确认豆包账号已开通 `doubao-seedream-4-5-251128` 模型权限

**日志里出现 `Blocked skill env overrides`**
- skill 的 `env.ARK_API_KEY` 会被 openclaw 安全层拦截
- 正确做法是用 `apiKey` 字段（安装向导会自动处理）
- 手动修复：`python3 -c "import json,os; path=os.path.expanduser('~/.openclaw/openclaw.json'); d=json.load(open(path)); [d['skills']['entries'][k].__setitem__('apiKey', d['skills']['entries'][k].pop('env',{}).get('ARK_API_KEY','')) for k in d['skills']['entries'] if 'clawpersona' in k]; json.dump(d, open(path,'w'), indent=2)"`

**语音生成失败**
- 需要网络访问 Microsoft Edge TTS 服务
- 检查：`uv run --with edge-tts python3 -c "import edge_tts; print('ok')"`

**图片生成超时**
- 豆包生图较慢，超时设置为 5 分钟，耐心等待
- 检查网络连接是否正常

## 8. 更新

```bash
cd ~/ws/ClawPersona
git pull origin main
npm install -g .
# 重新安装 skills（保留 API key）
node -e "
const { installSkills, ensureDirectories } = require('./src/installer');
const cfg = JSON.parse(require('fs').readFileSync(require('os').homedir()+'/.openclaw/openclaw.json'));
const key = Object.values(cfg.skills.entries).find(e => e.apiKey)?.apiKey;
ensureDirectories();
installSkills(['suwan','linyan','gujin','xiayang','tangguo','lushenchen','jiangyu','shenmobai','guyan','xuzhiyuan'], key);
console.log('updated');
"
```
