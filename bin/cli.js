#!/usr/bin/env node

/**
 * ClawPersona - Multi-Persona Installer for OpenClaw
 *
 * npx clawpersona@latest
 */

const fs = require("fs");
const path = require("path");
const readline = require("readline");
const { execSync } = require("child_process");

// Import local modules
const installer = require("../src/installer");
const switcher = require("../src/persona-switcher");

// Colors for terminal output
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
};

const c = (color, text) => `${colors[color]}${text}${colors.reset}`;

function log(msg) {
  console.log(msg);
}

function logStep(step, msg) {
  console.log(`\n${c("cyan", `[${step}]`)} ${msg}`);
}

function logSuccess(msg) {
  console.log(`${c("green", "✓")} ${msg}`);
}

function logError(msg) {
  console.log(`${c("red", "✗")} ${msg}`);
}

function logInfo(msg) {
  console.log(`${c("blue", "→")} ${msg}`);
}

function logWarn(msg) {
  console.log(`${c("yellow", "!")} ${msg}`);
}

// Create readline interface
function createPrompt() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

// Ask a question and get answer
function ask(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim());
    });
  });
}

// Print banner
function printBanner() {
  console.log(`
${c("magenta", "┌─────────────────────────────────────────────────┐")}
${c("magenta", "│")}  ${c("bright", "ClawPersona")} - Multi-Persona AI Assistant  ${c("magenta", "│")}
${c("magenta", "└─────────────────────────────────────────────────┘")}

${c("dim", "Give your OpenClaw agent multiple personalities!")}
`);
}

// Print personas list
function printPersonas() {
  log(`${c("bright", "Available Personas:")}`);
  log("");
  
  const personas = installer.getAllPersonas();
  Object.entries(personas).forEach(([key, p], i) => {
    log(`  ${c("cyan", `${i + 1}.`)} ${p.name} ${p.emoji}`);
    log(`     ${c("dim", p.description)}`);
  });
  
  log("");
}

// Get API key
async function getApiKey(rl) {
  logStep("Setup", "API Key Configuration");

  const DOUBAO_URL = "https://console.volcengine.com/ark/";

  log(`\nClawPersona uses Doubao (豆包) Seedream API for image generation.`);
  log(`${c("cyan", "→")} Get your key from: ${c("bright", DOUBAO_URL)}\n`);

  const openIt = await ask(rl, "Open Doubao console in browser? (Y/n): ");

  if (openIt.toLowerCase() !== "n") {
    logInfo("Opening browser...");
    const platform = process.platform;
    let cmd;
    if (platform === "darwin") {
      cmd = `open "${DOUBAO_URL}"`;
    } else if (platform === "win32") {
      cmd = `start "${DOUBAO_URL}"`;
    } else {
      cmd = `xdg-open "${DOUBAO_URL}"`;
    }
    try {
      execSync(cmd, { stdio: "ignore" });
    } catch {
      logWarn("Could not open browser automatically");
    }
  }

  log("");
  const apiKey = await ask(rl, "Enter your ARK_API_KEY: ");

  if (!apiKey) {
    logError("API key is required!");
    return null;
  }

  if (apiKey.length < 10) {
    logWarn("That key looks too short. Make sure you copied the full key.");
  }

  logSuccess("API key received");
  return apiKey;
}

// Select personas to install
async function selectPersonas(rl) {
  logStep("Install", "Select Personas to Install");

  printPersonas();

  const choices = [
    { key: "all", label: "Install ALL personas (5女+5男)" },
    { key: "suwan", label: "苏婉 🎨 - 文艺插画师" },
    { key: "linyan", label: "林妍 💼 - 职场投行经理" },
    { key: "gujin", label: "顾瑾 📚 - 知性博士生" },
    { key: "xiayang", label: "夏阳 🏃‍♀️ - 活力健身教练" },
    { key: "tangguo", label: "糖果 🍬 - 甜酷设计学生" },
    { key: "lushenchen", label: "陆景深 🏢 - 霸道总裁CEO" },
    { key: "jiangyu", label: "江屿 🎸 - 音乐才子" },
    { key: "shenmobai", label: "沈墨白 ⚕️ - 温柔医生" },
    { key: "guyan", label: "顾言 🏀 - 阳光学弟" },
    { key: "xuzhiyuan", label: "许知远 🎨 - 神秘画家" },
  ];

  log("Options:");
  choices.forEach((c, i) => {
    log(`  ${i}. ${c.label}`);
  });

  log("");
  const answer = await ask(rl, "Enter numbers (comma-separated) or 'all': ");

  let selectedKeys = [];

  if (answer.toLowerCase() === "all" || answer === "0") {
    selectedKeys = Object.keys(installer.getAllPersonas());
  } else {
    const indices = answer.split(",").map((s) => parseInt(s.trim()));
    for (const idx of indices) {
      if (idx >= 1 && idx <= 5) {
        selectedKeys.push(choices[idx].key);
      }
    }
  }

  if (selectedKeys.length === 0) {
    logWarn("No valid selection. Installing all personas.");
    selectedKeys = Object.keys(installer.getAllPersonas());
  }

  return selectedKeys;
}

// Select default persona
async function selectDefaultPersona(rl, installedKeys) {
  logStep("Default", "Select Default Persona");

  const personas = installer.getAllPersonas();
  const installed = installedKeys.map((k) => ({ key: k, ...personas[k] }));

  log("Installed personas:");
  installed.forEach((p, i) => {
    log(`  ${i + 1}. ${p.name} ${p.emoji} - ${p.description}`);
  });

  log("");
  const answer = await ask(rl, "Select default persona (number): ");
  const idx = parseInt(answer) - 1;

  if (idx >= 0 && idx < installed.length) {
    return installed[idx].key;
  }

  return installed[0].key;
}

// Main installation flow
async function runInstall(rl) {
  printBanner();

  // Check prerequisites
  logStep("1/5", "Checking prerequisites...");
  const prereqs = installer.checkPrerequisites();

  if (!prereqs.openclaw) {
    logError("OpenClaw CLI not found!");
    logInfo("Install with: npm install -g openclaw");
    return false;
  }
  logSuccess("OpenClaw CLI found");

  if (!prereqs.directory) {
    logWarn("OpenClaw directory not found. Creating...");
  }
  installer.ensureDirectories();
  logSuccess("Directory structure ready");

  // Get API key
  const apiKey = await getApiKey(rl);
  if (!apiKey) return false;

  // Select personas
  const selectedKeys = await selectPersonas(rl);

  // Install skills
  logStep("3/5", "Installing skills...");
  const results = installer.installSkills(selectedKeys, apiKey);
  results.forEach((r) => {
    logSuccess(`Installed: ${r.persona.name} ${r.persona.emoji}`);
  });

  // Select and set default persona
  const defaultKey = await selectDefaultPersona(rl, selectedKeys);

  // Generate PERSONA.md
  logStep("4/5", "Configuring default persona...");
  installer.generatePersonaMd(defaultKey);
  logSuccess(`Default persona: ${installer.getPersona(defaultKey).name}`);

  // Inject into SOUL.md
  logStep("5/5", "Injecting persona into SOUL.md...");
  installer.injectPersona(defaultKey);
  logSuccess("SOUL.md updated");

  // Print summary
  printSummary(results, defaultKey);

  return true;
}

// Switch persona flow
async function runSwitch(rl, targetPersona) {
  const key = switcher.parsePersonaInput(targetPersona);

  if (!key) {
    logError(`Unknown persona: ${targetPersona}`);
    logInfo("Available: suwan, linyan, gujin, xiayang, tangguo");
    return false;
  }

  const result = switcher.switchPersona(key);

  if (result.success) {
    logSuccess(result.message);
    log("");
    log(c("bright", result.greeting));
    return true;
  } else {
    logError(result.error);
    return false;
  }
}

// List personas
function runList() {
  const list = switcher.listPersonas();
  log(c("bright", list.formatted));
}

// Print summary
function printSummary(results, defaultKey) {
  const defaultPersona = installer.getPersona(defaultKey);

  console.log(`
${c("green", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")}
${c("bright", "  Installation Complete!")}
${c("green", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")}

${c("cyan", "Installed Personas:")}
${results.map((r) => `  ${r.persona.emoji} ${r.persona.name}`).join("\n")}

${c("cyan", "Default Persona:")}
  ${defaultPersona.emoji} ${defaultPersona.name} - ${defaultPersona.description}

${c("cyan", "Configuration Files:")}
  ${installer.paths.PERSONA_MD}
  ${installer.paths.SOUL_MD}

${c("yellow", "Try these commands:")}
  /persona 苏婉    - Switch to Su Wan
  /persona 林妍    - Switch to Lin Yan
  /persona-list    - List all personas

${c("dim", "Your agent now has multiple personalities!")}
`);
}

// Show help
function showHelp() {
  console.log(`
${c("bright", "ClawPersona CLI")}

Usage:
  npx clawpersona@latest           Run interactive installer
  npx clawpersona@latest install   Install personas
  npx clawpersona@latest switch <name>  Switch persona
  npx clawpersona@latest list      List personas
  npx clawpersona@latest --help    Show this help

Personas (女性):
  suwan      - 苏婉 🎨 文艺插画师
  linyan     - 林妍 💼 职场投行经理
  gujin      - 顾瑾 📚 知性博士生
  xiayang    - 夏阳 🏃‍♀️ 活力健身教练
  tangguo    - 糖果 🍬 甜酷设计学生

Personas (男性):
  lushenchen - 陆景深 🏢 霸道总裁CEO
  jiangyu    - 江屿 🎸 音乐才子
  shenmobai  - 沈墨白 ⚕️ 温柔医生
  guyan      - 顾言 🏀 阳光学弟
  xuzhiyuan  - 许知远 🎨 神秘画家
`);
}

// Main function
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const rl = createPrompt();

  try {
    if (command === "--help" || command === "-h") {
      showHelp();
      rl.close();
      return;
    }

    if (command === "switch" || command === "s") {
      const personaName = args[1];
      if (!personaName) {
        logError("Please specify a persona name");
        logInfo("Example: npx clawpersona switch 苏婉");
        rl.close();
        process.exit(1);
      }
      const success = await runSwitch(rl, personaName);
      rl.close();
      process.exit(success ? 0 : 1);
    }

    if (command === "list" || command === "ls") {
      runList();
      rl.close();
      return;
    }

    if (command === "install" || command === "i" || !command) {
      const success = await runInstall(rl);
      rl.close();
      process.exit(success ? 0 : 1);
    }

    logError(`Unknown command: ${command}`);
    showHelp();
    rl.close();
    process.exit(1);
  } catch (error) {
    logError(`Error: ${error.message}`);
    console.error(error);
    rl.close();
    process.exit(1);
  }
}

// Run
main();
