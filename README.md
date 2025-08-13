# Whisper 字幕生成器

一个基于 OpenAI Whisper 和 stable-ts 的音视频字幕自动生成工具，具有图形界面，支持多种音视频格式。

## 功能特性

- 支持多种音视频格式：
  - 音频：mp3, wav, flac, aac, ogg, m4a
  - 视频：mp4, avi, mov, mkv, flv, wmv, webm
- 图形用户界面，操作简单
- 支持多种语言识别（中文、英语、日语、韩语等）
- 多种 Whisper 模型大小选择（tiny, base, small, medium, large）
- 自动检测并使用 stable-ts 优化时间轴精度
- 优雅降级机制：未安装 stable-ts 时自动使用原始 Whisper
- 支持批量处理多个文件
- 可自定义输出目录

## 目录结构

```
音视频语音字幕识别/
├── 启动字幕生成器_新.bat     # 程序启动批处理文件
├── launcher.py              # 程序启动器
└── whisper_subtitle_app/    # 主程序目录
    ├── gui.py               # 图形界面
    ├── main.py              # 主程序入口
    ├── subtitle_generator.py # 字幕生成核心逻辑
    ├── __pycache__/         # Python 编译缓存
    ├── build/               # 打包构建目录
    ├── dist/                # 打包发布目录
    └── venv/                # Python 虚拟环境
```

## 安装与配置

### 环境要求

- Windows 系统
- Python 3.7+
- ffmpeg（用于音视频处理）

### 安装步骤

1. 确保系统已安装 ffmpeg 并添加到 PATH 环境变量中
2. 程序已包含预配置的 Python 虚拟环境，无需额外安装依赖

### 启动程序

双击 `启动字幕生成器_新.bat` 文件即可启动程序。

## 使用说明

1. **添加文件**：
   - 点击"添加文件"按钮选择要处理的音视频文件
   - 支持多选，可一次添加多个文件

2. **配置参数**：
   - **语言**：选择音频语言，"自动检测"适用于多语言混合的音频
   - **模型大小**：选择 Whisper 模型大小
     - tiny/small：速度快，资源占用少，准确性较低
     - base：平衡选择，推荐一般使用
     - medium/large：准确性高，但需要更多内存和处理时间
   - **输出目录**：选择生成的字幕文件保存位置

3. **开始处理**：
   - 点击"开始处理"按钮开始生成字幕
   - 处理过程中可在日志区域查看进度和详细信息

4. **查看结果**：
   - 处理完成后，可在指定的输出目录中找到生成的 .srt 字幕文件
   - 字幕文件名与原始音视频文件名一致

## 技术说明

### stable-ts 优化

程序会自动检测是否安装了 stable-ts 库：
- 如果已安装：使用 stable-whisper 进行转录，提供更精确的时间轴
- 如果未安装：自动降级到原始 OpenAI Whisper

在日志中会显示使用的转录方法：
```
检测到 stable-ts，将使用优化的时间戳...
正在使用 stable-ts优化版 进行语音识别 ...
语音识别完成。使用的转录方法: stable-ts优化版
```

### 核心模块

#### subtitle_generator.py
字幕生成核心逻辑，包含以下主要函数：
- `process_file()`: 处理单个文件的主函数
- `transcribe_audio()`: 音频转录函数，支持 stable-ts 优化
- `generate_srt()`: 生成 SRT 字幕文件

#### gui.py
图形界面实现，基于 tkinter 构建。

#### main.py
程序主入口。

#### launcher.py
程序启动器，负责设置虚拟环境并启动主程序。

## 开发与调试

### 代码结构

程序采用模块化设计，便于维护和扩展：
- `subtitle_generator.py`：核心逻辑模块
- `gui.py`：界面模块
- `main.py`：主入口模块
- `launcher.py`：启动器模块

### 修改代码

1. **添加新支持的格式**：
   - 修改 `subtitle_generator.py` 中的 `SUPPORTED_FORMATS` 字典

2. **调整 stable-ts 参数**：
   - 在 `subtitle_generator.py` 的 `transcribe_audio()` 函数中修改 stable-ts 相关参数

3. **界面修改**：
   - 修改 `gui.py` 文件

### 调试技巧

1. **查看详细日志**：
   - 程序运行时的所有操作都会在日志区域显示
   - 包括模型加载、设备使用、转录过程等信息

2. **Python 虚拟环境**：
   - 程序使用独立的虚拟环境，位于 `whisper_subtitle_app/venv/`
   - 如需安装新依赖，可使用：
     ```
     whisper_subtitle_app\venv\Scripts\pip install 包名
     ```

3. **清除缓存**：
   - 如需清除 Python 编译缓存，可删除 `whisper_subtitle_app/__pycache__/` 目录

### 常见问题

1. **程序启动失败**：
   - 检查是否正确安装了 ffmpeg
   - 确认虚拟环境目录 `whisper_subtitle_app/venv/` 是否存在

2. **字幕时间轴不准确**：
   - 尝试使用更大的模型（medium/large）
   - 确认是否成功使用 stable-ts 优化
   - 检查音频质量，必要时进行预处理

3. **处理速度慢**：
   - 使用较小的模型（tiny/base）
   - 确认是否启用了 GPU 加速（CUDA）

## 版本信息

- 当前版本：1.0
- 更新日期：2025年8月11日

## 许可证

本项目仅供个人学习和研究使用，请遵守相关法律法规。