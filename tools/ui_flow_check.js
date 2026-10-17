// tools/ui_flow_check.js
// 作为 browser_check.mjs 的第 4 个参数执行，用于验证交互链路。示例：
//   node tools/browser_check.mjs http://127.0.0.1:8000/ ui_flow.png @tools/ui_flow_check.js
//
// 该文件在页面上下文中运行，因此不能使用 import/require。
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const status = () => window.shaderLab.getStatus();
  const assert = (condition, message) => {
    if (!condition) throw new Error("UI_FLOW_FAIL: " + message);
  };
  const results = {};

  assert(status().ready, "初始 WebGL 未就绪");
  assert(status().ingestions.length === 2, "默认摄入记录数量不为 2");
  assert(status().timelineDuration === 600, "默认时间轴不为 600 分钟");

  // 1) 在 T+900 添加记录，时间轴自动扩展
  document.getElementById("inp-time").value = "900";
  document.getElementById("inp-dose").value = "10";
  document.getElementById("btn-add-ingestion").click();
  await sleep(900);
  results.afterAdd = {
    count: status().ingestions.length,
    duration: status().timelineDuration,
    sliderMax: document.getElementById("slider-time").max
  };
  assert(results.afterAdd.count === 3, "添加摄入记录失败");
  assert(results.afterAdd.duration === 1260, "时间轴未扩展到 1260 分钟");
  assert(results.afterAdd.sliderMax === "1260", "时间滑块 max 未同步");

  // 2) 跳到 T+900 并确认标签
  window.shaderLab.setTime(900);
  await sleep(700);
  results.time900 = {
    current: status().currentTimeMinutes,
    label: document.getElementById("lbl-current-time").textContent
  };
  assert(results.time900.current === 900, "setTime(900) 未生效");
  assert(results.time900.label.includes("T+ 900 min"), "时间标签未更新");

  // 3) 恢复协同示例
  document.getElementById("btn-preset-candyflip").click();
  await sleep(900);
  results.preset = {
    count: status().ingestions.length,
    duration: status().timelineDuration,
    current: status().currentTimeMinutes
  };
  assert(results.preset.count === 3, "预设记录数量错误");
  assert(results.preset.duration === 600, "预设后时间轴未回到 600");
  assert(results.preset.current === 235, "预设当前时刻错误");

  // 4) 手动覆盖 / 取消覆盖
  const slider = document.querySelector('[data-param="warp_amplitude"]');
  slider.value = "1";
  slider.dispatchEvent(new Event("input", { bubbles: true }));
  results.manualOn = {
    checked: document.getElementById("chk-manual").checked,
    warp: status().uniforms.warp_amplitude
  };
  assert(results.manualOn.checked, "手动覆盖未勾选");
  assert(results.manualOn.warp === 1, "手动覆盖值未生效");

  const checkbox = document.getElementById("chk-manual");
  checkbox.checked = false;
  checkbox.dispatchEvent(new Event("change", { bubbles: true }));
  await sleep(900);
  results.manualOff = {
    checked: checkbox.checked,
    warp: status().uniforms.warp_amplitude,
    hud: document.getElementById("hud-mode").textContent
  };
  assert(!results.manualOff.checked, "取消覆盖失败");
  assert(results.manualOff.warp > 0 && results.manualOff.warp < 1, "取消覆盖后未回到 PK-PD 参数");
  assert(results.manualOff.hud.includes("PK-PD DRIVEN"), "HUD 未回到 PK-PD 模式");

  // 5) 清空记录
  document.getElementById("btn-clear-ingestions").click();
  await sleep(900);
  results.cleared = {
    count: status().ingestions.length,
    duration: status().timelineDuration,
    symmetry: status().uniforms.symmetry_order,
    synergy: document.getElementById("val-synergy").textContent
  };
  assert(results.cleared.count === 0, "清空摄入记录失败");
  assert(results.cleared.duration === 600, "空记录时时间轴应回到 600");
  assert(results.cleared.symmetry === 1, "空记录时对称阶数应为 1");

  // 6) 画布尺寸变化 -> FBO 重建
  const canvas = document.getElementById("gl-canvas");
  canvas.style.width = "320px";
  canvas.style.height = "240px";
  await sleep(800);
  results.smallResize = status().resolution;
  assert(results.smallResize.w === 320 && results.smallResize.h === 240, "缩小画布后分辨率未更新");

  canvas.style.width = "";
  canvas.style.height = "";
  await sleep(800);
  results.restoredResize = status().resolution;
  assert(results.restoredResize.w > 320, "恢复画布尺寸后分辨率未恢复");

  // 7) 上下文丢失 / 恢复
  const gl = canvas.getContext("webgl2");
  const extension = gl.getExtension("WEBGL_lose_context");
  if (extension) {
    extension.loseContext();
    await sleep(700);
    results.afterLoss = { contextLost: status().contextLost, ready: status().ready };
    assert(results.afterLoss.contextLost, "上下文丢失事件未生效");

    extension.restoreContext();
    await sleep(1500);
    results.afterRestore = {
      contextLost: status().contextLost,
      ready: status().ready,
      errors: status().errors
    };
    assert(!results.afterRestore.contextLost, "上下文恢复事件未生效");
    assert(results.afterRestore.ready, "上下文恢复后 WebGL 未就绪");
    assert(results.afterRestore.errors.length === 0, "上下文恢复过程中产生错误");
  } else {
    results.contextLoss = "WEBGL_lose_context 不可用，跳过";
  }

  // 8) 空间立体主义示例
  document.getElementById("btn-cubism-demo").click();
  await sleep(700);
  results.cubism = {
    checked: document.getElementById("chk-manual").checked,
    cubism: status().uniforms.cubism,
    shatter: status().uniforms.shatter,
    hud: document.getElementById("hud-extra").textContent
  };
  assert(results.cubism.checked, "立体主义示例未开启手动覆盖");
  assert(Math.abs(results.cubism.cubism - 0.85) < 0.001, "立体主义示例未设置 cubism=0.85");
  assert(results.cubism.shatter > 0.5, "立体主义示例未设置碎片化");
  assert(results.cubism.hud.includes("cub:0.85"), "HUD 未显示立体主义参数");

  // 9) 新增现象学档案
  const archiveSelect = document.getElementById("sel-archive");
  const archiveCount = archiveSelect.options.length;
  archiveSelect.value = "5";
  archiveSelect.dispatchEvent(new Event("change", { bubbles: true }));
  await sleep(250);
  results.archive = {
    count: archiveCount,
    text: document.getElementById("archive-detail").textContent.replace(/\s+/g, " ").slice(0, 120)
  };
  assert(results.archive.count === 8, "现象学档案数量不是 8");
  assert(results.archive.text.includes("立体主义"), "新增空间立体主义档案未显示");

  // 10) 参考集浏览器
  document.getElementById("btn-reference").click();
  await sleep(1400);
  const referenceModal = document.getElementById("reference-modal");
  const referenceButtons = [...document.querySelectorAll("#reference-list button")];
  results.reference = {
    visible: !referenceModal.classList.contains("hidden"),
    count: referenceButtons.length,
    meta: document.getElementById("reference-meta").textContent
  };
  assert(results.reference.visible, "参考集弹窗未打开");
  assert(results.reference.count === 25, "参考集物质数量不是 25");
  assert(results.reference.meta.includes("1,619") || results.reference.meta.includes("1619"), "参考集元数据未加载");

  const ketamineButton = referenceButtons.find((button) => button.textContent.includes("Ketamine"));
  assert(ketamineButton, "参考集列表中找不到 Ketamine");
  ketamineButton.click();
  await sleep(1000);
  const referenceTitle = document.querySelector("#reference-detail h3")?.textContent || "";
  results.reference.detailTitle = referenceTitle;
  assert(referenceTitle.includes("Ketamine"), "参考集详情未加载 Ketamine");

  document.getElementById("btn-close-reference").click();
  assert(referenceModal.classList.contains("hidden"), "参考集弹窗未关闭");

  assert(status().errors.length === 0, "交互流程产生运行时错误");
  return JSON.stringify(results, null, 2);
})()
