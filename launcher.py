# -*- coding: utf-8 -*-
"""
Whisper 字幕生成器启动器
通过Python脚本启动，避免.bat文件的编码和路径问题。
"""

import os
import sys
import subprocess

def main():
    # 1. 确定项目根目录 (launcher.py所在的目录)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(current_dir, "whisper_subtitle_app")
    
    if not os.path.exists(project_dir):
        print(f"错误: 未找到项目目录 '{project_dir}'")
        input("按回车键退出...")
        sys.exit(1)

    # 2. 确定虚拟环境Python解释器路径
    venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        print(f"错误: 未找到虚拟环境Python解释器 '{venv_python}'")
        print("请确保已正确创建Python虚拟环境。")
        input("按回车键退出...")
        sys.exit(1)

    # 3. 确定主程序脚本路径
    main_script = os.path.join(project_dir, "main.py")
    if not os.path.exists(main_script):
        print(f"错误: 未找到主程序脚本 '{main_script}'")
        input("按回车键退出...")
        sys.exit(1)

    # 4. 检查ffmpeg (可选，但最好提示)
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("已检测到 ffmpeg。")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("警告: 系统PATH中未找到 ffmpeg。语音识别可能需要它。")
        print("请确保已安装 ffmpeg 并将其添加到系统环境变量 PATH 中。\n")

    # 5. 使用虚拟环境中的Python解释器启动主程序
    print("正在从虚拟环境启动 Whisper 字幕生成器...")
    print(f"虚拟环境: {os.path.dirname(os.path.dirname(venv_python))}")
    print(f"Python解释器: {venv_python}")
    print(f"主程序: {main_script}\n")
    
    try:
        # 使用 subprocess.run 来启动主程序，并等待其完成
        # cwd 设置工作目录为主程序所在目录
        result = subprocess.run([venv_python, main_script], cwd=project_dir)
        
        if result.returncode == 0:
            print("\n程序已正常退出。")
        else:
            print(f"\n程序异常退出，退出代码: {result.returncode}")
            
    except Exception as e:
        print(f"\n启动主程序时发生错误: {e}")
        
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()