import subprocess
import sys

def build():
    print("📦 正在安装打包依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pystray", "pillow"])

    print("\n🔨 正在将 Gemini Bridge 编译为独立无窗口可执行程序 (EXE)...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=GeminiBridge",
        "local_daemon/gemini_bridge_daemon.py"
    ]
    subprocess.run(cmd)
    print("\n🎉 打包完成！请在 dist/ 目录下查看生成的 GeminiBridge.exe！")

if __name__ == "__main__":
    build()
