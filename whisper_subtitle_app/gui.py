import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from subtitle_generator import process_file, SUPPORTED_FORMATS

class SubtitleGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper 字幕生成器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)  # 允许窗口调整大小

        # 存储选中的文件路径
        self.selected_files = []

        # Whisper支持的语言列表 (简化版，包含常见语言)
        # 可以从whisper.tokenizer.LANGUAGES获取完整列表
        self.languages = {
            "自动检测": None,
            "中文": "zh",
            "英语": "en",
            "日语": "ja",
            "韩语": "ko",
            "法语": "fr",
            "德语": "de",
            "西班牙语": "es",
            "俄语": "ru",
            "阿拉伯语": "ar",
            "印地语": "hi"
        }
        
        # Whisper模型大小
        self.model_sizes = ['tiny', 'base', 'small', 'medium', 'large']

        self.create_widgets()

    def create_widgets(self):
        # --- 文件选择区域 ---
        file_frame = tk.LabelFrame(self.root, text="文件选择")
        file_frame.pack(fill="x", padx=10, pady=5)

        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, height=6)
        self.file_listbox.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)

        scrollbar = tk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame_file = tk.Frame(file_frame)
        btn_frame_file.pack(fill="x", padx=5, pady=5)

        self.btn_select_files = tk.Button(btn_frame_file, text="添加文件", command=self.select_files)
        self.btn_select_files.pack(side="left", padx=(0, 5))

        self.btn_clear_files = tk.Button(btn_frame_file, text="清空列表", command=self.clear_files)
        self.btn_clear_files.pack(side="left")

        # --- 配置区域 ---
        config_frame = tk.LabelFrame(self.root, text="配置")
        config_frame.pack(fill="x", padx=10, pady=5)

        # 语言选择
        lang_label = tk.Label(config_frame, text="语言:")
        lang_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.lang_var = tk.StringVar(value="自动检测")
        lang_options = list(self.languages.keys())
        self.lang_menu = ttk.Combobox(config_frame, textvariable=self.lang_var, values=lang_options, state="readonly", width=15)
        self.lang_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # 模型大小选择
        model_label = tk.Label(config_frame, text="模型大小:")
        model_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.model_var = tk.StringVar(value="base")
        model_options = self.model_sizes
        self.model_menu = ttk.Combobox(config_frame, textvariable=self.model_var, values=model_options, state="readonly", width=10)
        self.model_menu.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # 输出目录
        output_dir_label = tk.Label(config_frame, text="输出目录:")
        output_dir_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "output_subtitles"))
        self.output_dir_entry = tk.Entry(config_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        config_frame.columnconfigure(1, weight=1) # 让Entry可以拉伸

        self.btn_browse_output = tk.Button(config_frame, text="浏览...", command=self.browse_output_dir)
        self.btn_browse_output.grid(row=1, column=3, padx=5, pady=5)

        # --- 控制按钮 ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.btn_start = tk.Button(control_frame, text="开始处理", command=self.start_processing, bg='lightblue')
        self.btn_start.pack(side="left", padx=5)

        self.btn_exit = tk.Button(control_frame, text="退出", command=self.root.quit)
        self.btn_exit.pack(side="right", padx=5)

        # --- 日志/进度区域 ---
        log_frame = tk.LabelFrame(self.root, text="日志")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, wrap="word", height=10, state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

    def log(self, message):
        """在日志区域添加信息"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END) # 自动滚动到底部
        self.log_text.config(state="disabled")
        self.root.update_idletasks() # 刷新界面

    def select_files(self):
        """打开文件选择对话框"""
        # 构建文件类型过滤器
        all_supported = SUPPORTED_FORMATS['audio'] + SUPPORTED_FORMATS['video']
        filetypes = [
            ("支持的文件", [f"*.{ext}" for ext in all_supported]),
            ("音频文件", [f"*.{ext}" for ext in SUPPORTED_FORMATS['audio']]),
            ("视频文件", [f"*.{ext}" for ext in SUPPORTED_FORMATS['video']]),
            ("所有文件", ["*.*"])
        ]
        
        file_paths = filedialog.askopenfilenames(
            title="选择音视频文件",
            filetypes=filetypes
        )
        
        if file_paths:
            unique_new_files = set(file_paths) - set(self.selected_files)
            self.selected_files.extend(unique_new_files)
            self.update_file_listbox()

    def clear_files(self):
        """清空文件列表"""
        self.selected_files.clear()
        self.update_file_listbox()

    def update_file_listbox(self):
        """更新文件列表框显示"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(file_path))

    def browse_output_dir(self):
        """浏览并选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择字幕输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)

    def start_processing(self):
        """启动处理线程"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要处理的文件。")
            return

        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录。")
            return

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        selected_language_key = self.lang_var.get()
        language_code = self.languages.get(selected_language_key)
        
        model_size = self.model_var.get()

        # 在新线程中运行处理逻辑，避免阻塞GUI
        self.btn_start.config(state="disabled", text="处理中...")
        processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(self.selected_files, output_dir, language_code, model_size),
            daemon=True
        )
        processing_thread.start()

    def process_files_thread(self, files, output_dir, language, model_size):
        """在后台线程中处理文件"""
        try:
            total_files = len(files)
            self.log(f"开始处理 {total_files} 个文件...")
            success_count = 0

            for i, file_path in enumerate(files):
                self.log(f"[{i+1}/{total_files}] 正在处理: {os.path.basename(file_path)}")
                try:
                    if process_file(file_path, output_dir, language=language, model_size=model_size):
                        self.log(f"[{i+1}/{total_files}] 成功: {os.path.basename(file_path)}")
                        success_count += 1
                    else:
                        self.log(f"[{i+1}/{total_files}] 失败: {os.path.basename(file_path)}")
                except Exception as e:
                    self.log(f"[{i+1}/{total_files}] 错误: {os.path.basename(file_path)} - {e}")

            self.log(f"处理完成。成功: {success_count}/{total_files}")
            messagebox.showinfo("完成", f"处理完成。\n成功: {success_count}/{total_files}")
        except Exception as e:
            error_msg = f"处理过程中发生未预期的错误: {e}"
            self.log(error_msg)
            messagebox.showerror("错误", error_msg)
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.btn_start.config(state="normal", text="开始处理"))

def main():
    root = tk.Tk()
    app = SubtitleGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()