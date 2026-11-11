(function () {
  const DAEMON_URL = "http://127.0.0.1:8765/dispatch";
  const BRIDGE_TOKEN = "gdb-local-bridge-2026";

  function injectButtons() {
    const responseBlocks = document.querySelectorAll("model-response");

    responseBlocks.forEach((block) => {
      if (block.dataset.bridgeInjected) return;
      block.dataset.bridgeInjected = "true";

      const actionBar = document.createElement("div");
      actionBar.className = "gemini-bridge-action-bar";

      const btn = document.createElement("button");
      btn.className = "gemini-bridge-btn";
      btn.innerHTML = '<span class="bridge-icon">⚡</span> 派发到本地 Agent 执行';

      const statusSpan = document.createElement("span");
      statusSpan.className = "gemini-bridge-status";

      btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.innerHTML = '<span class="bridge-spinner">⏳</span> 正在通知本地电脑执行...';
        statusSpan.innerText = "";

        let payloadText = "";
        const codeBlock = block.querySelector("pre, code");
        if (codeBlock) {
          payloadText = codeBlock.innerText.trim();
        } else {
          payloadText = block.innerText.trim();
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 35000);

        try {
          const res = await fetch(DAEMON_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Bridge-Token": BRIDGE_TOKEN
            },
            body: JSON.stringify({
              source: "gemini_web",
              content: payloadText,
              timestamp: new Date().toISOString()
            }),
            signal: controller.signal
          });
          clearTimeout(timeoutId);

          const data = await res.json();
          if (data.status === "success") {
            btn.innerHTML = '<span class="bridge-icon">✅</span> 执行成功';
            btn.className = "gemini-bridge-btn success";
            statusSpan.innerText = data.summary || "执行完成";
            statusSpan.style.color = "#10b981";

            if (data.output) {
              let logBox = block.querySelector(".gemini-bridge-log");
              if (!logBox) {
                logBox = document.createElement("pre");
                logBox.className = "gemini-bridge-log";
                block.appendChild(logBox);
              }
              logBox.innerText = "[执行输出]:\n" + data.output;
            }
          } else {
            throw new Error(data.message || "执行失败");
          }
        } catch (err) {
          clearTimeout(timeoutId);
          btn.innerHTML = '<span class="bridge-icon">❌</span> 派发失败';
          btn.className = "gemini-bridge-btn error";
          statusSpan.innerText = err.name === "AbortError" ? "执行超时" : "未检测到本地服务 (请先启动 GeminiBridge.exe)";
          statusSpan.style.color = "#ef4444";
        } finally {
          setTimeout(() => { btn.disabled = false; }, 3000);
        }
      });

      actionBar.appendChild(btn);
      actionBar.appendChild(statusSpan);
      block.appendChild(actionBar);
    });
  }

  const observer = new MutationObserver(() => injectButtons());
  observer.observe(document.body, { childList: true, subtree: true });
  setTimeout(injectButtons, 1200);
})();
