"""
Whisper 字幕生成器主入口
"""
import os
import sys

def main():
    # 将当前脚本所在目录添加到Python路径中
    # 这样可以确保即使在打包后也能正确导入模块
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    try:
        # 导入并运行GUI
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"导入模块时出错: {e}")
        input("按回车键退出...")
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()