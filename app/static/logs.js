async function getJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return await res.json();
}

async function loginLogs() {
  const password = document.getElementById("password-input").value;
  const data = await getJSON("/api/logs/auth", {
    method: "POST",
    body: JSON.stringify({ password }),
  });

  if (data.ok) {
    sessionStorage.setItem("homie_logs_auth", "ok");
    window.location.href = "/logs/view";
  } else {
    document.getElementById("login-result").textContent = "密码错误";
  }
}

async function refreshLogs() {
  if (window.location.pathname.includes("/logs/view")) {
    if (sessionStorage.getItem("homie_logs_auth") !== "ok") {
      window.location.href = "/logs";
      return;
    }
    const data = await getJSON("/api/logs");
    document.getElementById("logs").innerHTML = data.logs.map(l => `
      <div class="feed-item">
        <div class="feed-head"><strong>${l.category}</strong><span class="badge">${new Date(l.ts * 1000).toLocaleString()}</span></div>
        <div style="margin-top:8px;">${l.message}</div>
      </div>
    `).join("") || "<div class='muted'>暂无日志</div>";
  }
}

if (window.location.pathname.includes("/logs/view")) {
  refreshLogs();
  setInterval(refreshLogs, 5000);
}
