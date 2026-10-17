#!/usr/bin/env node
// tools/browser_check.mjs
// 无依赖的 Chrome DevTools Protocol 冒烟测试：捕获控制台/异常、读取着色器状态并截图。
//
// 用法：
//   node tools/browser_check.mjs [url] [screenshot.png]
// 默认：
//   url            http://127.0.0.1:8000/
//   screenshot     ./browser_check.png
//
// 退出码：0 = 页面与 WebGL 正常；1 = 有异常 / WebGL 未就绪。
import { spawn } from "node:child_process";
import { existsSync, writeFileSync, rmSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const URL_TARGET = process.argv[2] || "http://127.0.0.1:8000/";
const SCREENSHOT = process.argv[3] || "browser_check.png";
const WINDOW_SIZE = process.env.BROWSER_WINDOW || "1600,900";
// 第 4 个参数可以是表达式，也可以写成 @路径 从文件读取（避免 shell 引号转义问题）
const PRE_EVAL_ARG = process.argv[4] || "";
const PRE_EVAL = PRE_EVAL_ARG.startsWith("@") ? readFileSync(PRE_EVAL_ARG.slice(1), "utf8") : PRE_EVAL_ARG;
const PORT = 9333 + Math.floor(Math.random() * 200);
const PROFILE = mkdtempSync(join(tmpdir(), "shaderlab-cdp-"));

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].filter(Boolean);

const chromePath = CHROME_CANDIDATES.find((candidate) => existsSync(candidate));
if (!chromePath) {
  console.error("未找到 Chrome/Edge，可通过 CHROME_PATH 环境变量指定。");
  process.exit(2);
}

const chrome = spawn(chromePath, [
  "--headless=new",
  "--enable-unsafe-swiftshader",
  "--hide-scrollbars",
  "--no-first-run",
  "--no-default-browser-check",
  "--disable-extensions",
  "--disable-background-networking",
  `--window-size=${WINDOW_SIZE}`,
  ...(process.env.BROWSER_FAKE_MEDIA ? ["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"] : []),
  `--user-data-dir=${PROFILE}`,
  `--remote-debugging-port=${PORT}`,
  "about:blank"
], { stdio: "ignore" });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForDevtools() {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (response.ok) return;
    } catch (_error) {
      // Chrome 尚未就绪
    }
    await sleep(100);
  }
  throw new Error("等待 Chrome DevTools 超时");
}

let exitCode = 0;
let ws;
try {
  await waitForDevtools();

  const response = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(URL_TARGET)}`, { method: "PUT" });
  const target = await response.json();

  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });

  let messageId = 0;
  const pending = new Map();
  const consoleLines = [];
  const errors = [];

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
      return;
    }
    if (message.method === "Runtime.consoleAPICalled") {
      const text = message.params.args
        .map((arg) => (arg.value !== undefined ? String(arg.value) : arg.description || arg.type))
        .join(" ");
      consoleLines.push(`[console.${message.params.type}] ${text}`);
      if (message.params.type === "error") errors.push(text);
    }
    if (message.method === "Runtime.exceptionThrown") {
      const detail = message.params.exceptionDetails;
      errors.push(detail.exception?.description || detail.text || "未知异常");
    }
    if (message.method === "Log.entryAdded") {
      const entry = message.params.entry;
      if (entry.level === "error") errors.push(`${entry.source}: ${entry.text}`);
    }
  };

  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++messageId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });

  await send("Runtime.enable");
  await send("Page.enable");
  await send("Log.enable");
  await sleep(5000); // 等待 API、WebGL 初始化与若干帧渲染

  if (PRE_EVAL) {
    const evalResult = await send("Runtime.evaluate", { expression: PRE_EVAL, awaitPromise: true, returnByValue: true });
    if (evalResult.exceptionDetails) {
      errors.push(evalResult.exceptionDetails.text || "预执行表达式抛出异常");
    } else if (evalResult.result?.value !== undefined) {
      console.log("Pre-eval result:\n" + evalResult.result.value);
    }
    await sleep(1200);
  }

  const statusResult = await send("Runtime.evaluate", {
    expression: "JSON.stringify(window.shaderLab ? window.shaderLab.getStatus() : null)",
    returnByValue: true
  });
  const status = statusResult.result?.value ? JSON.parse(statusResult.result.value) : null;

  const screenshot = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(SCREENSHOT, Buffer.from(screenshot.data, "base64"));

  console.log("Console:");
  if (consoleLines.length === 0) console.log("  (无输出)");
  consoleLines.forEach((line) => console.log("  " + line));

  console.log("\nStatus:");
  console.log(JSON.stringify(status, null, 2));

  if (errors.length > 0) {
    console.log("\nErrors:");
    errors.forEach((line) => console.log("  - " + line));
    exitCode = 1;
  }
  if (!status || !status.ready) {
    console.log("\nWebGL 未就绪");
    exitCode = 1;
  } else if (status.errors.length > 0) {
    exitCode = 1;
  }

  console.log(`\n截图: ${SCREENSHOT}`);
} catch (error) {
  console.error("browser_check 失败:", error);
  exitCode = 1;
} finally {
  if (ws) ws.close();
  chrome.kill();
  await sleep(300);
  try {
    rmSync(PROFILE, { recursive: true, force: true });
  } catch (_error) {
    // Windows 上 Chrome 可能仍占用 profile，忽略
  }
  process.exit(exitCode);
}
