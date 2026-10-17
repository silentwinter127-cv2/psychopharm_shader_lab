// tools/audio_check.js
// 作为 browser_check.mjs 的第 4 个参数执行，验证 Web Audio 声音模拟链路：
//   node tools/browser_check.mjs http://127.0.0.1:8000/ audio.png @tools/audio_check.js
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const status = () => window.shaderLab.getStatus();
  const assert = (condition, message) => {
    if (!condition) throw new Error("AUDIO_FAIL: " + message);
  };

  await sleep(500);
  document.getElementById("btn-audio-toggle").click();
  await sleep(1600);
  const on = status().audio;
  await sleep(600);
  const later = status().audio;

  assert(on.enabled, "声音模拟未开启");
  assert(on.contextState === "running", "AudioContext 未运行: " + on.contextState);
  assert(on.profile && on.profile.active, "没有活动的听觉画像");
  assert(later.meter > 0.01, "音频分析器没有能量");
  assert(on.params, "没有音频参数诊断");
  assert(on.params.cutoff < 8000, "默认示例的低通未明显介入: " + (on.params && on.params.cutoff));
  assert(on.params.wet > 0.25, "默认示例的延迟湿声过低: " + (on.params && on.params.wet));
  assert(status().errors.length === 0, "声音模拟产生运行时错误");

  return JSON.stringify({
    enabled: on.enabled,
    contextState: on.contextState,
    sourceName: on.sourceName,
    meter: later.meter,
    params: on.params,
    profile: {
      clarity: on.profile.clarity,
      suppression: on.profile.suppression,
      distortion: on.profile.distortion,
      hallucination: on.profile.hallucination,
      synaesthesia: on.profile.synaesthesia,
      dissociation: on.profile.dissociation
    }
  }, null, 2);
})()
