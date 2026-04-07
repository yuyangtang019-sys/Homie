const chatFeed = [];

async function getJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return await res.json();
}

function deviceStateText(d) {
  if (d.type === "light") return d.state.power === "on" ? "开启" : "关闭";
  if (d.type === "aircon") return `${d.state.power === "on" ? "开启" : "关闭"} / ${d.state.mode} / ${d.state.target_temp}°C`;
  if (d.type === "curtain") return d.state.position === "open" ? "已打开" : "已关闭";
  if (d.type === "door") return d.state.lock === "locked" ? "已锁定" : "已解锁";
  return JSON.stringify(d.state);
}

function commandButton(d) {
  if (d.type === "light") return `<button onclick="sendDeviceCommand('${d.id}','${d.state.power === 'on' ? 'turn_off' : 'turn_on'}')">切换</button>`;
  if (d.type === "aircon") return `<button onclick="sendDeviceCommand('${d.id}','${d.state.power === 'on' ? 'turn_off' : 'turn_on'}')">切换</button>`;
  if (d.type === "curtain") return `<button onclick="sendDeviceCommand('${d.id}','${d.state.position === 'open' ? 'close' : 'open'}')">切换</button>`;
  if (d.type === "door") return `<button onclick="sendDeviceCommand('${d.id}','${d.state.lock === 'locked' ? 'unlock' : 'lock'}')">切换</button>`;
  return "";
}

async function refreshAll() {
  const deviceData = await getJSON("/api/devices");
  const envData = await getJSON("/api/devices/environment");
  const ruleData = await getJSON("/api/rules");

  document.getElementById("devices").innerHTML = deviceData.devices.map(d => `
    <div class="device-card">
      <div class="device-head"><strong>${d.name}</strong><span class="badge">${d.type}</span></div>
      <div class="device-state" style="margin-top:10px;">${deviceStateText(d)}</div>
      <div class="actions">${commandButton(d)}</div>
    </div>
  `).join("");

  document.getElementById("current-time").textContent = envData.environment.current_time;
  document.getElementById("current-temp").textContent = envData.environment.temperature + "°C";
  document.getElementById("current-light").textContent = envData.environment.light + " lx";
  document.getElementById("current-presence").textContent = envData.environment.presence ? "是" : "否";
  document.getElementById("panel-temp").textContent = envData.environment.temperature;
  document.getElementById("env-time").value = envData.environment.current_time;
  document.getElementById("env-temp").value = envData.environment.temperature;
  document.getElementById("env-light").value = envData.environment.light;
  document.getElementById("env-presence").value = String(envData.environment.presence);

  document.getElementById("rules").innerHTML = ruleData.rules.map(r => `
    <div class="feed-item">
      <div class="feed-head"><strong>${r.name}</strong><span class="badge">${r.trigger_type}</span></div>
      <div class="muted" style="margin-top:8px;">触发：${JSON.stringify(r.trigger)}</div>
      <div class="muted" style="margin-top:8px;">动作：${JSON.stringify(r.actions)}</div>
      <div class="actions"><button class="secondary" onclick="deleteRule('${r.id}')">删除规则</button></div>
    </div>
  `).join("") || "<div class='muted'>暂无规则</div>";

  renderChatFeed();
}

function renderChatFeed() {
  document.getElementById("chat-feed").innerHTML = chatFeed.map(item => `
    <div class="feed-item">
      <div class="feed-head"><strong>${item.role === 'user' ? '你' : 'Homie'}</strong><span class="badge">${item.type}</span></div>
      <div style="margin-top:8px;">${item.text}</div>
    </div>
  `).join("") || "<div class='muted'>暂无对话记录</div>";
}

async function previewChat() {
  const prompt = document.getElementById("chat-input").value;
  const data = await getJSON("/api/agent/preview", { method: "POST", body: JSON.stringify({ prompt }) });
  document.getElementById("chat-preview").textContent = JSON.stringify(data, null, 2);
}

async function sendChat() {
  const prompt = document.getElementById("chat-input").value.trim();
  if (!prompt) return;

  chatFeed.unshift({ role: "user", type: "input", text: prompt });

  const data = await getJSON("/api/agent/chat", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });

  document.getElementById("chat-result").textContent = data.message || JSON.stringify(data);
  chatFeed.unshift({ role: "assistant", type: data.mode || "result", text: data.message || "已处理" });

  document.getElementById("chat-input").value = "";
  await refreshAll();
}

async function sendDeviceCommand(deviceId, command) {
  await getJSON(`/api/devices/${deviceId}/command`, {
    method: "POST",
    body: JSON.stringify({ command, params: {} }),
  });
  await refreshAll();
}

async function updateEnvironment() {
  const current_time = document.getElementById("env-time").value;
  const temperature = Number(document.getElementById("env-temp").value);
  const light = Number(document.getElementById("env-light").value);
  const presence = document.getElementById("env-presence").value === "true";
  await getJSON("/api/devices/environment", {
    method: "POST",
    body: JSON.stringify({ current_time, temperature, light, presence }),
  });
  await refreshAll();
}

async function evaluateRules() {
  await getJSON("/api/rules/evaluate", { method: "POST" });
  await refreshAll();
}

async function deleteRule(ruleId) {
  await fetch(`/api/rules/${ruleId}`, { method: "DELETE" });
  await refreshAll();
}

refreshAll();
setInterval(refreshAll, 5000);
