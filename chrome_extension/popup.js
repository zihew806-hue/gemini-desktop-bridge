document.addEventListener("DOMContentLoaded", async () => {
  const badge = document.getElementById("daemon-badge");
  const status = document.getElementById("daemon-status");

  try {
    const res = await fetch("http://127.0.0.1:8765/health");
    const data = await res.json();
    if (data.status === "ok") {
      badge.className = "status-badge online";
      status.innerText = "在线 (8765)";
      status.style.color = "#10b981";
    }
  } catch (e) {
    badge.className = "status-badge offline";
    status.innerText = "未启动";
    status.style.color = "#ef4444";
  }
});
