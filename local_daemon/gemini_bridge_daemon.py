#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Desktop Bridge - Local System Tray Daemon

SECURITY MODEL (IMPORTANT):
    This daemon binds to 127.0.0.1 only and accepts /dispatch requests
    EXCLUSIVELY from a Chrome extension origin (chrome-extension://*) and
    requires a shared bridge token (X-Bridge-Token header). It intentionally
    does NOT use `Access-Control-Allow-Origin: *` and does NOT listen on
    0.0.0.0. Without these guards, any website you visit could silently
    execute commands on your machine (local RCE). Do not weaken this.
"""

import os
import sys
import json
import threading
import tempfile
import subprocess
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw
import pystray

PORT = 8765

# Shared secret between the extension and the daemon. This is defense-in-depth;
# the real protection is the chrome-extension:// origin restriction below.
BRIDGE_TOKEN = "gdb-local-bridge-2026"
ALLOWED_ORIGIN_PREFIX = "chrome-extension://"


# ----------------- 本地中继 HTTP 服务 -----------------

class BridgeHandler(BaseHTTPRequestHandler):
    def _allowed_origin(self):
        origin = self.headers.get("Origin", "")
        if origin.startswith(ALLOWED_ORIGIN_PREFIX):
            return origin
        return "null"

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", self._allowed_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Bridge-Token")
        self.send_header("Vary", "Origin")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "port": PORT}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/dispatch":
            self.send_response(404)
            self.end_headers()
            return

        # Reject any caller that is not the Chrome extension.
        if self._allowed_origin() == "null":
            self.send_response(403)
            self.end_headers()
            return

        # Require the shared bridge token.
        if self.headers.get("X-Bridge-Token", "") != BRIDGE_TOKEN:
            self.send_response(403)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        raw = data.get("content", "").strip()
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"[{timestamp}] 📥 收到派发指令: {raw[:100]}...")

        output, summary = self.execute_smart(raw)

        self.send_response(200)
        self._send_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "success",
            "summary": summary,
            "output": output
        }).encode("utf-8"))

    def execute_smart(self, content):
        """智能解析：支持直接 Windows 命令批处理与 Agent 任务派发"""
        # 1. 提取代码块
        code_text = content
        if "```" in content:
            parts = content.split("```")
            for i in range(1, len(parts), 2):
                snippet = parts[i].strip()
                lines = snippet.split("\n", 1)
                if len(lines) > 1 and lines[0].lower() in ["bat", "cmd", "dos", "powershell", "ps1", "sh", "bash"]:
                    code_text = lines[1].strip()
                else:
                    code_text = snippet
                break

        # 2. 检查是否为原生 Shell 指令
        lines = [l.strip() for l in code_text.splitlines() if l.strip()]
        is_direct_cmd = any(
            line.lower().startswith(("echo ", "cd ", "mkdir ", "dir ", "copy ", "del ", "python ", "agy "))
            or ">" in line or ">>" in line
            for line in lines
        )

        if is_direct_cmd and len(lines) <= 6:
            # 走本地 Windows 批处理无转义执行
            with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False, encoding="utf-8") as tf:
                tf.write("@echo off\nchcp 65001 >nul\n" + "\n".join(lines) + "\n")
                bat_path = tf.name
            try:
                proc = subprocess.run(["cmd.exe", "/c", bat_path], capture_output=True, text=True, encoding="utf-8", timeout=15)
                os.remove(bat_path)
                out = proc.stdout or proc.stderr or "本地命令已成功执行完成！"
                return out, "本地 Shell 执行成功"
            except Exception as e:
                if os.path.exists(bat_path):
                    os.remove(bat_path)
                return str(e), "执行失败"

        # 3. 走 Antigravity Headless 执行
        safe_prompt = content.replace('"', '""')
        cmd = f'agy -p "{safe_prompt}" --mode auto'
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", timeout=35)
            out = proc.stdout or proc.stderr or "Antigravity 执行完成"
            return out, "Antigravity 成功执行"
        except subprocess.TimeoutExpired:
            return "执行超时 (35秒)", "超时"
        except Exception as e:
            return str(e), "执行异常"

    def log_message(self, fmt, *args):
        # 静默默认访问日志，避免控制台噪音
        return


# ----------------- 系统托盘与运行管理 -----------------

def create_tray_icon():
    image = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # 画一个渐变质感的蓝色电光圆标
    draw.ellipse((4, 4, 60, 60), fill=(15, 23, 42))
    draw.ellipse((8, 8, 56, 56), fill=(14, 165, 233))
    draw.polygon([(32, 12), (20, 36), (32, 36), (28, 52), (44, 28), (32, 28)], fill=(255, 255, 255))
    return image


def run_tray():
    icon_image = create_tray_icon()

    def open_gemini(icon, item):
        webbrowser.open("https://gemini.google.com/")

    def open_github(icon, item):
        webbrowser.open("https://github.com/zihew806-hue/gemini-desktop-bridge")

    def exit_app(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("🟢 Gemini Bridge: 运行中 (8765)", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🌐 打开 Google Gemini 网页", open_gemini),
        pystray.MenuItem("☕ 支持作者 / GitHub 仓库", open_github),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ 退出服务", exit_app)
    )

    icon = pystray.Icon("GeminiBridge", icon_image, "Gemini Desktop Bridge (运行中)", menu)
    icon.run()


if __name__ == "__main__":
    # 后台启动 HTTP 监听
    server = HTTPServer(("127.0.0.1", PORT), BridgeHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # 主线程启动系统托盘图标
    run_tray()
