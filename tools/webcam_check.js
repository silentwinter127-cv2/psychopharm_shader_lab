// tools/webcam_check.js
// 摄像头链路回归脚本（需要 Chrome 虚拟摄像头）：
//   $env:BROWSER_FAKE_MEDIA = "1"
//   node tools/browser_check.mjs http://127.0.0.1:8000/ webcam.png @tools/webcam_check.js
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const status = () => window.shaderLab.getStatus();
  const assert = (condition, message) => {
    if (!condition) throw new Error("WEBCAM_FAIL: " + message);
  };
  const button = document.getElementById("btn-webcam");
  const video = document.getElementById("webcam-video");
  const results = {};

  // 开启
  button.click();
  await sleep(1500);
  results.on = {
    active: status().webcamActive,
    source: status().source,
    label: button.textContent,
    videoReady: video.readyState
  };
  assert(results.on.active, "摄像头未开启");
  assert(results.on.source === "webcam", "输入源未切换为 webcam");
  assert(results.on.label === "关闭摄像头", "按钮文案未切换");
  assert(results.on.videoReady >= 2, "视频帧尚不可用");

  // 关闭
  button.click();
  await sleep(700);
  results.off = { active: status().webcamActive, label: button.textContent };
  assert(!results.off.active, "摄像头未关闭");
  assert(results.off.label === "开启摄像头", "关闭后按钮文案错误");

  // 再次开启，并把 uniform 归零以便截图确认画面来自摄像头
  button.click();
  await sleep(1500);
  Object.keys(status().uniforms).forEach((key) => {
    window.shaderLab.setUniform(key, key === "symmetry_order" ? 1 : 0);
  });
  await sleep(700);
  results.restarted = status().webcamActive;
  assert(results.restarted, "摄像头无法重新开启");
  assert(status().errors.length === 0, "摄像头流程产生运行时错误");

  return JSON.stringify(results, null, 2);
})()
