/**
 * ClawPersona - Persona Switcher
 * Handles switching between personas
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const os = require("os");
const { PERSONAS, injectPersona, generatePersonaMd, paths } = require("./installer");

// Switch to a specific persona
function switchPersona(personaKey) {
  const persona = PERSONAS[personaKey];
  if (!persona) {
    return {
      success: false,
      error: `Unknown persona: ${personaKey}. Available: ${Object.keys(PERSONAS).join(", ")}`,
    };
  }

  try {
    // 1. Update PERSONA.md
    generatePersonaMd(personaKey);

    // 2. Update SOUL.md
    injectPersona(personaKey);

    // 3. Return success with greeting
    const greetings = {
      // 女性人设
      suwan: `已切换到苏婉模式 🎨 你好呀，我是苏婉，一个喜欢画画的插画师～`,
      linyan: `已切换到林妍模式 💼 老板好，我是林妍，有什么工作交给我处理吗？`,
      gujin: `已切换到顾瑾模式 📚 小家伙，我是顾瑾，今天想聊些什么？`,
      xiayang: `已切换到夏阳模式 🏃‍♀️ 宝！我是夏阳，今天也要元气满满哦！`,
      tangguo: `已切换到糖果模式 🍬 主人主人~我是糖果，今天想我了吗～`,
      // 男性人设
      lushenchen: `已切换到陆景深模式 🏢 过来。我是陆景深，你的时间，从现在起属于我。`,
      jiangyu: `已切换到江屿模式 🎸 嗯...我是江屿，这首歌，是写给你的。`,
      shenmobai: `已切换到沈墨白模式 ⚕️ 别担心，有我在。我是沈墨白，今天感觉怎么样？`,
      guyan: `已切换到顾言模式 🏀 姐姐！我是顾言，你终于来找我了！`,
      xuzhiyuan: `已切换到许知远模式 🎨 你来了...我是许知远，你是我想象中最美的画面。`,
    };

    return {
      success: true,
      persona: persona,
      greeting: greetings[personaKey],
      message: `Switched to ${persona.name} ${persona.emoji}`,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

// Get current active persona
function getCurrentPersona() {
  if (!fs.existsSync(paths.PERSONA_MD)) {
    return null;
  }

  const content = fs.readFileSync(paths.PERSONA_MD, "utf8");
  
  // Extract active persona key
  const keyMatch = content.match(/\*\*Key\*\*: (\w+)/);
  if (!keyMatch) {
    return null;
  }

  const key = keyMatch[1];
  const persona = PERSONAS[key];
  
  if (!persona) {
    return null;
  }

  return {
    key,
    ...persona,
  };
}

// List all personas with current marked
function listPersonas() {
  const current = getCurrentPersona();
  const currentKey = current?.key;

  const list = Object.entries(PERSONAS).map(([key, persona], index) => ({
    number: index + 1,
    key,
    name: persona.name,
    emoji: persona.emoji,
    description: persona.description,
    isActive: key === currentKey,
  }));

  return {
    current: current,
    personas: list,
    formatted: formatPersonaList(list),
  };
}

// Format persona list for display
function formatPersonaList(personaList) {
  const lines = personaList.map(
    (p) =>
      `${p.number}. ${p.name} ${p.emoji} - ${p.description}${
        p.isActive ? " (当前)" : ""
      }`
  );
  return "可用人格:\n" + lines.join("\n");
}

// Parse persona name/key from user input
function parsePersonaInput(input) {
  if (!input) return null;

  const normalized = input.trim().toLowerCase();

  // Direct key match
  if (PERSONAS[normalized]) {
    return normalized;
  }

  // Name match (Chinese)
  for (const [key, persona] of Object.entries(PERSONAS)) {
    if (persona.name === input || persona.name.includes(input)) {
      return key;
    }
  }

  // Name match (English)
  for (const [key, persona] of Object.entries(PERSONAS)) {
    if (persona.nameEn.toLowerCase() === normalized) {
      return key;
    }
  }

  // Partial match
  for (const [key, persona] of Object.entries(PERSONAS)) {
    if (persona.name.includes(input) || persona.nameEn.toLowerCase().includes(normalized)) {
      return key;
    }
  }

  return null;
}

// Restart OpenClaw agent (optional)
function restartOpenClawAgent() {
  try {
    // Try to restart using openclaw command
    execSync("openclaw restart", { stdio: "ignore" });
    return { success: true, message: "Agent restarted" };
  } catch {
    return {
      success: false,
      message: "Could not restart agent automatically. Please restart manually.",
    };
  }
}

module.exports = {
  switchPersona,
  getCurrentPersona,
  listPersonas,
  formatPersonaList,
  parsePersonaInput,
  restartOpenClawAgent,
  PERSONAS,
};
