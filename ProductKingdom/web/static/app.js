const stages = ["pm", "architect", "backend", "frontend", "qa"];
const stageNames = {
  pm: "产品经理（PM）",
  architect: "架构师（Architect）",
  backend: "后端开发（Backend）",
  frontend: "前端开发（Frontend）",
  qa: "测试工程师（QA）",
  done: "退朝"
};

let threadId = "";
let latestState = null;

const $ = (id) => document.getElementById(id);

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  window.setTimeout(() => el.classList.remove("show"), 3200);
}

function setBusy(isBusy) {
  const done = latestState && latestState.status === "done";
  $("startBtn").disabled = isBusy;
  $("approveBtn").disabled = isBusy || !threadId || done;
  $("rejectBtn").disabled = isBusy || !threadId || done;
  updateArtifactButtons();
  if (isBusy) toast("众臣正在拟奏，请稍候……");
}

function updateArtifactButtons() {
  const ready = latestState && latestState.artifactReady && latestState.artifact;
  $("sourceBtn").disabled = !ready;
  $("useBtn").disabled = !ready;
  $("downloadBtn").disabled = !ready;
}

function updateStages(state) {
  document.querySelectorAll(".stage-list li").forEach((item) => {
    const stage = item.dataset.stage;
    const status = item.querySelector("strong");
    item.classList.remove("active", "done");

    if (state.outputs && state.outputs[stage]) {
      item.classList.add("done");
      status.textContent = "已准奏";
    } else if (stage === state.stage) {
      item.classList.add("active");
      status.textContent = "进行中";
    } else {
      status.textContent = "待启奏";
    }
  });
}

function renderState(state) {
  latestState = state;
  threadId = state.threadId || threadId;

  $("statStage").textContent = state.stageName || stageNames[state.stage] || "尚未下旨";
  $("statRevisions").textContent = `${state.currentRevisions || 0} / ${state.maxRevisions || 3}`;
  $("statCompleted").textContent = `${state.completedCount || 0} / ${state.totalCount || 5}`;

  updateStages(state);

  if (state.status === "done") {
    $("draftTitle").textContent = "退朝汇总";
    $("draftIntro").textContent = "五位大臣均已启奏完毕。";
    $("draft").classList.remove("empty");
    $("draft").textContent = "所有奏折已批准。点击下方按钮查看完整汇总。";
    $("approveBtn").disabled = true;
    $("rejectBtn").disabled = true;
    $("summaryBtn").disabled = false;
    updateArtifactButtons();
    showSummary();
    return;
  }

  $("draftTitle").textContent = `当前奏折（${state.stageName || stageNames[state.stage] || ""}启奏）`;
  $("draftIntro").textContent = `以下为 ${state.stageName || ""} 启奏之草案，陛下请批阅：`;
  $("draft").classList.remove("empty");
  $("draft").textContent = state.draft || "暂无奏折。";
  $("approveBtn").disabled = false;
  $("rejectBtn").disabled = false;
  $("summaryBtn").disabled = !state.outputs || Object.keys(state.outputs).length === 0;
  updateArtifactButtons();
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "请求失败");
  return data;
}

async function start() {
  const requirement = $("requirement").value.trim();
  if (!requirement) {
    toast("请陛下先写下产品需求。");
    return;
  }

  setBusy(true);
  try {
    const state = await postJson("/api/start", { requirement });
    $("feedback").value = "";
    $("feedbackCount").textContent = "0";
    renderState(state);
  } catch (err) {
    toast(err.message);
  } finally {
    setBusy(false);
  }
}

async function review(verdict) {
  if (!threadId) {
    toast("请先下旨开始上朝。");
    return;
  }

  const feedback = $("feedback").value.trim();
  if (verdict === "reject" && !feedback) {
    toast("驳回时请写下朱批意见。");
    return;
  }

  setBusy(true);
  try {
    const state = await postJson("/api/review", { threadId, verdict, feedback });
    $("feedback").value = "";
    $("feedbackCount").textContent = "0";
    renderState(state);
  } catch (err) {
    toast(err.message);
  } finally {
    setBusy(false);
  }
}

function showSummary() {
  if (!latestState || !latestState.outputs) return;
  const content = $("summaryContent");
  content.innerHTML = "";
  stages.forEach((stage) => {
    if (!latestState.outputs[stage]) return;
    const section = document.createElement("section");
    section.className = "summary-section";
    section.textContent = `${stageNames[stage]}\n\n${latestState.outputs[stage]}`;
    content.appendChild(section);
  });
  $("summaryDialog").showModal();
}

async function showSource() {
  if (!latestState || !latestState.artifact) {
    toast("产品源码尚未生成。");
    return;
  }

  try {
    const res = await fetch(latestState.artifact.sourceUrl);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "无法读取源码");
    $("sourceFileName").textContent = data.filename || "index.html";
    $("sourceCode").textContent = data.code || "";
    $("sourceDialog").showModal();
  } catch (err) {
    toast(err.message);
  }
}

function useProduct() {
  if (!latestState || !latestState.artifact) {
    toast("产品尚未生成。");
    return;
  }
  window.open(latestState.artifact.useUrl, "_blank", "noopener");
}

function downloadProduct() {
  if (!latestState || !latestState.artifact) {
    toast("产品下载包尚未生成。");
    return;
  }
  window.location.href = latestState.artifact.downloadUrl;
}

$("startBtn").addEventListener("click", start);
$("approveBtn").addEventListener("click", () => review("approve"));
$("rejectBtn").addEventListener("click", () => review("reject"));
$("summaryBtn").addEventListener("click", showSummary);
$("closeSummary").addEventListener("click", () => $("summaryDialog").close());
$("sourceBtn").addEventListener("click", showSource);
$("useBtn").addEventListener("click", useProduct);
$("downloadBtn").addEventListener("click", downloadProduct);
$("closeSource").addEventListener("click", () => $("sourceDialog").close());
$("feedback").addEventListener("input", (event) => {
  $("feedbackCount").textContent = event.target.value.length;
});
