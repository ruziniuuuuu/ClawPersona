/**
 * ClawPersona - Installer
 * Handles installation of persona skills and configuration
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const os = require("os");

// Paths
const HOME = os.homedir();
const OPENCLAW_DIR = path.join(HOME, ".openclaw");
const OPENCLAW_CONFIG = path.join(OPENCLAW_DIR, "openclaw.json");
const OPENCLAW_SKILLS_DIR = path.join(OPENCLAW_DIR, "skills");
const OPENCLAW_WORKSPACE = path.join(OPENCLAW_DIR, "workspace");
const SOUL_MD = path.join(OPENCLAW_WORKSPACE, "SOUL.md");
const PERSONA_MD = path.join(OPENCLAW_WORKSPACE, "PERSONA.md");

// Persona definitions
const PERSONAS = {
  // ── 女性人设 ──
  suwan: {
    name: "苏婉",
    nameEn: "Su Wan",
    emoji: "🎨",
    description: "文艺插画师",
    gender: "female",
    skillName: "clawpersona-suwan-selfie",
    soulTemplate: "soul-suwan.md",
  },
  linyan: {
    name: "林妍",
    nameEn: "Lin Yan",
    emoji: "💼",
    description: "职场投行经理",
    gender: "female",
    skillName: "clawpersona-linyan-selfie",
    soulTemplate: "soul-linyan.md",
  },
  gujin: {
    name: "顾瑾",
    nameEn: "Gu Jin",
    emoji: "📚",
    description: "知性博士生",
    gender: "female",
    skillName: "clawpersona-gujin-selfie",
    soulTemplate: "soul-gujin.md",
  },
  xiayang: {
    name: "夏阳",
    nameEn: "Xia Yang",
    emoji: "🏃‍♀️",
    description: "活力健身教练",
    gender: "female",
    skillName: "clawpersona-xiayang-selfie",
    soulTemplate: "soul-xiayang.md",
  },
  tangguo: {
    name: "糖果",
    nameEn: "Tang Guo",
    emoji: "🍬",
    description: "甜酷设计学生",
    gender: "female",
    skillName: "clawpersona-tangguo-selfie",
    soulTemplate: "soul-tangguo.md",
  },
  // ── 男性人设 ──
  lushenchen: {
    name: "陆景深",
    nameEn: "Lu Shenchen",
    emoji: "🏢",
    description: "霸道总裁 · 科技公司CEO",
    gender: "male",
    skillName: "clawpersona-lushenchen-selfie",
    soulTemplate: "soul-lushenchen.md",
  },
  jiangyu: {
    name: "江屿",
    nameEn: "Jiang Yu",
    emoji: "🎸",
    description: "音乐才子 · 独立音乐人",
    gender: "male",
    skillName: "clawpersona-jiangyu-selfie",
    soulTemplate: "soul-jiangyu.md",
  },
  shenmobai: {
    name: "沈墨白",
    nameEn: "Shen Mobai",
    emoji: "⚕️",
    description: "温柔医生 · 外科医生",
    gender: "male",
    skillName: "clawpersona-shenmobai-selfie",
    soulTemplate: "soul-shenmobai.md",
  },
  guyan: {
    name: "顾言",
    nameEn: "Gu Yan",
    emoji: "🏀",
    description: "阳光学弟 · 体育系大学生",
    gender: "male",
    skillName: "clawpersona-guyan-selfie",
    soulTemplate: "soul-guyan.md",
  },
  xuzhiyuan: {
    name: "许知远",
    nameEn: "Xu Zhiyuan",
    emoji: "🎨",
    description: "神秘画家 · 画家",
    gender: "male",
    skillName: "clawpersona-xuzhiyuan-selfie",
    soulTemplate: "soul-xuzhiyuan.md",
  },
};

// Get package root
function getPackageRoot() {
  return path.resolve(__dirname, "..");
}

// Read JSON file safely
function readJsonFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf8");
    return JSON.parse(content);
  } catch {
    return null;
  }
}

// Write JSON file with formatting
function writeJsonFile(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n");
}

// Deep merge objects
function deepMerge(target, source) {
  const result = { ...target };
  for (const key in source) {
    if (
      source[key] &&
      typeof source[key] === "object" &&
      !Array.isArray(source[key])
    ) {
      result[key] = deepMerge(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

// Copy directory recursively
function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Check if a command exists
function commandExists(cmd) {
  try {
    execSync(`which ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

// Check prerequisites
function checkPrerequisites() {
  const results = {
    openclaw: false,
    directory: false,
  };

  // Check OpenClaw CLI
  if (commandExists("openclaw")) {
    results.openclaw = true;
  }

  // Check ~/.openclaw directory
  if (fs.existsSync(OPENCLAW_DIR)) {
    results.directory = true;
  }

  return results;
}

// Ensure directory structure exists
function ensureDirectories() {
  fs.mkdirSync(OPENCLAW_DIR, { recursive: true });
  fs.mkdirSync(OPENCLAW_SKILLS_DIR, { recursive: true });
  fs.mkdirSync(OPENCLAW_WORKSPACE, { recursive: true });
}

// Install a single skill
function installSkill(personaKey, apiKey) {
  const persona = PERSONAS[personaKey];
  if (!persona) {
    throw new Error(`Unknown persona: ${personaKey}`);
  }

  const packageRoot = getPackageRoot();
  const skillSrc = path.join(packageRoot, "skills", persona.skillName);
  const skillDest = path.join(OPENCLAW_SKILLS_DIR, persona.skillName);

  // Check if skill exists in package
  if (!fs.existsSync(skillSrc)) {
    throw new Error(`Skill not found: ${skillSrc}`);
  }

  // Remove existing installation
  if (fs.existsSync(skillDest)) {
    fs.rmSync(skillDest, { recursive: true, force: true });
  }

  // Copy skill files
  copyDir(skillSrc, skillDest);

  // Update OpenClaw config
  updateOpenClawConfig(persona.skillName, apiKey);

  return skillDest;
}

// Update OpenClaw config
function updateOpenClawConfig(skillName, apiKey) {
  let config = readJsonFile(OPENCLAW_CONFIG) || {};

  // Merge skill configuration
  const skillConfig = {
    skills: {
      entries: {
        [skillName]: {
          enabled: true,
          apiKey: apiKey,
        },
      },
    },
  };

  config = deepMerge(config, skillConfig);

  // Ensure skills directory is in load paths
  if (!config.skills) {
    config.skills = {};
  }
  if (!config.skills.load) {
    config.skills.load = {};
  }
  if (!config.skills.load.extraDirs) {
    config.skills.load.extraDirs = [];
  }
  if (!config.skills.load.extraDirs.includes(OPENCLAW_SKILLS_DIR)) {
    config.skills.load.extraDirs.push(OPENCLAW_SKILLS_DIR);
  }

  writeJsonFile(OPENCLAW_CONFIG, config);
}

// Install multiple skills
function installSkills(personaKeys, apiKey) {
  const results = [];
  for (const key of personaKeys) {
    const dest = installSkill(key, apiKey);
    results.push({ key, dest, persona: PERSONAS[key] });
  }
  return results;
}

// Generate PERSONA.md
function generatePersonaMd(activePersonaKey) {
  const activePersona = PERSONAS[activePersonaKey];
  if (!activePersona) {
    throw new Error(`Unknown persona: ${activePersonaKey}`);
  }

  const content = `# PERSONA.md - Current Active Persona

## Active Persona

- **Name**: ${activePersona.name} ${activePersona.emoji}
- **Name (English)**: ${activePersona.nameEn}
- **Key**: ${activePersonaKey}
- **Description**: ${activePersona.description}
- **Skill**: ${activePersona.skillName}

## All Available Personas

${Object.entries(PERSONAS)
  .map(
    ([key, p]) =>
      `- ${p.name} ${p.emoji} (${key}) - ${p.description}${
        key === activePersonaKey ? " **[ACTIVE]**" : ""
      }`
  )
  .join("\n")}

## Installation Info

- **Installed at**: ${new Date().toISOString()}
- **Package**: clawpersona

---

_To switch persona, use the /persona command or run: npx clawpersona@latest_
`;

  fs.mkdirSync(path.dirname(PERSONA_MD), { recursive: true });
  fs.writeFileSync(PERSONA_MD, content);

  return PERSONA_MD;
}

// Inject persona into SOUL.md
function injectPersona(personaKey) {
  const persona = PERSONAS[personaKey];
  if (!persona) {
    throw new Error(`Unknown persona: ${personaKey}`);
  }

  const packageRoot = getPackageRoot();
  const templatePath = path.join(
    packageRoot,
    "templates",
    persona.soulTemplate
  );

  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templatePath}`);
  }

  const personaText = fs.readFileSync(templatePath, "utf8");

  // Ensure SOUL.md exists
  if (!fs.existsSync(SOUL_MD)) {
    fs.mkdirSync(path.dirname(SOUL_MD), { recursive: true });
    fs.writeFileSync(SOUL_MD, "# Agent Soul\n\n");
  }

  // Check if persona section already exists
  let currentSoul = fs.readFileSync(SOUL_MD, "utf8");

  // Remove all existing ClawPersona sections (handles duplicates and old "Clawra Persona:" format)
  currentSoul = currentSoul.replace(/\n## Claw[rR]a? Persona:[\s\S]*/g, "");
  currentSoul = currentSoul.replace(/\n## ClawPersona:[\s\S]*/g, "");

  // Append new persona section
  const newSection = `\n## ClawPersona: ${persona.name} ${persona.emoji}\n\n${personaText.replace(
    /## ClawPersona:.*\n/,
    ""
  )}`;

  fs.writeFileSync(SOUL_MD, currentSoul.trim() + "\n" + newSection);

  return SOUL_MD;
}

// Get list of installed persona skills
function getInstalledSkills() {
  const installed = [];
  for (const [key, persona] of Object.entries(PERSONAS)) {
    const skillPath = path.join(OPENCLAW_SKILLS_DIR, persona.skillName);
    if (fs.existsSync(skillPath)) {
      installed.push(key);
    }
  }
  return installed;
}

// Get active persona from PERSONA.md
function getActivePersona() {
  if (!fs.existsSync(PERSONA_MD)) {
    return null;
  }

  const content = fs.readFileSync(PERSONA_MD, "utf8");
  const match = content.match(/\*\*Key\*\*: (\w+)/);
  if (match) {
    return match[1];
  }
  return null;
}

// Get all personas info
function getAllPersonas() {
  return PERSONAS;
}

// Get single persona info
function getPersona(key) {
  return PERSONAS[key];
}

module.exports = {
  PERSONAS,
  checkPrerequisites,
  ensureDirectories,
  installSkill,
  installSkills,
  generatePersonaMd,
  injectPersona,
  getInstalledSkills,
  getActivePersona,
  getAllPersonas,
  getPersona,
  paths: {
    OPENCLAW_DIR,
    OPENCLAW_CONFIG,
    OPENCLAW_SKILLS_DIR,
    OPENCLAW_WORKSPACE,
    SOUL_MD,
    PERSONA_MD,
  },
};
