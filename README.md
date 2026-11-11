# ⚡ Gemini Desktop Bridge

<p align="center">
  <b>一键将 Google Gemini 网页端的决策大脑，无缝连接至本地桌面物理执行端。</b><br>
  Gemini 负责懂你与长记忆，本地 Agent (Antigravity / Shell / DeepSeek) 负责物理动手。
</p>

---

## 🌟 为什么要做这个项目？

- **Google Gemini 的优势**：拥有超长上下文、个人邮件与云盘记忆、每天大量免费请求；
- **但传统执行的痛点**：网页里的 AI 没有手脚，用户必须反复“人肉复制代码、下载文件、在窗口间疯狂切换”。
- **Gemini Desktop Bridge 的解法**：在 `gemini.google.com` 网页中一键直通本地物理电脑，直接调起本地 Shell、Python、AutoCAD、ComfyUI 和 Antigravity 执行，彻底消灭中间搬运！

---

## 🚀 极速上手（只需 30 秒）

### 步骤 1：下载并运行本地客户端
1. 前往 [Releases](https://github.com/zihew806-hue/gemini-desktop-bridge/releases) 下载最新的 **`GeminiBridge.exe`**；
2. 双击打开，它会自动静默最小化到 Windows 右下角系统托盘（带 🟢 在线呼吸灯）。无需安装任何 Python 依赖！

> 想自己打包？在仓库根目录运行 `python build_exe.py` 即可生成 `dist/GeminiBridge.exe`（单文件、无黑窗口）。

### 步骤 2：安装 Chrome 扩展
1. 打开 Chrome 访问 `chrome://extensions/`，开启右上角的 **【开发者模式】**；
2. 点击左上角 **【加载已解压的扩展程序】**，选择本仓库的 `chrome_extension` 文件夹。

### 步骤 3：体验一键执行
打开 [Google Gemini 网页](https://gemini.google.com/)，在任意回复下方直接点击：
👉 **【⚡ 派发到本地 Agent 执行】**！

---

## 🔒 安全模型（务必先读）

这是一个**会在你本机执行命令**的工具，请理解它的信任边界：

1. **本地中继守护进程只监听 `127.0.0.1`**，不对外网开放；
2. **`/dispatch` 接口仅接受来自 Chrome 扩展来源（`chrome-extension://*`）的请求**，并强制校验共享令牌 `X-Bridge-Token`；
3. 原始设计中的 `Access-Control-Allow-Origin: *` 已被**移除**——否则任何你访问的网页都能静默让你本机跑命令（本地 RCE）。请勿改回 `*`。

⚠️ **固有风险提醒**：由于扩展会把 Gemini 的回答内容派发到本地执行，请只对你信任的对话内容点击“执行”。不要对来路不明的提示词或包含破坏性指令（如 `del /format` 等）的回答点执行。执行本地 Shell 命令时，守护进程只会处理行数 ≤ 6 且以常见命令前缀开头的直接指令；其余内容会交给本地 Agent（`agy`）处理。

---

## ☕ Support the Author（支持作者）

本项目**完全免费且开源**，不设任何付费门槛或功能封锁。
如果你觉得这个小工具帮你省掉了每天切屏搬砖的痛苦，欢迎请作者喝杯咖啡 ☕，支持作者持续迭代支持更多 Agent！

| 微信赞赏 (WeChat Pay) | 支付宝打赏 (Alipay) |
| :---: | :---: |
| <img src="wechat_pay.png" width="220" alt="微信赞赏码"> | <img src="alipay.png" width="220" alt="支付宝收款码"> |

> 扫码请作者喝杯咖啡 ☕，感谢支持！

---

## 📁 项目结构

```text
gemini-desktop-bridge/
├── .gitignore
├── LICENSE
├── README.md
├── build_exe.py
├── local_daemon/
│   ├── gemini_bridge_daemon.py      # 系统托盘守护进程（HTTP 中继 + 智能派发）
│   └── requirements.txt
└── chrome_extension/
    ├── manifest.json
    ├── content.js
    ├── content.css
    ├── popup.html
    └── popup.js
```

---

## 📄 License

MIT License © 2026 王梓赫 (Zihe Wang)
