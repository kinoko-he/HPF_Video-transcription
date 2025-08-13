# HPF Video Transcription

这是一个基于 OpenAI Whisper 的音视频字幕生成工具，带有图形用户界面 (GUI)。

## 功能

- 支持多种音频和视频格式。
- 可选择不同的 Whisper 模型大小以平衡速度和准确性。
- 支持多种语言的识别。
- 可选的字幕行智能分割功能，避免单行字幕过长。
- 图形用户界面，操作简单。

## 安装

1.  **克隆或下载本仓库**:
    ```bash
    git clone https://github.com/kinoko-he/HPF_Video-transcription.git
    cd HPF_Video-transcription
    ```

2.  **确保你有一个可用的 Python 环境** (推荐 Python 3.8 或更高版本)。

3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
    这将安装以下必要的库：
    - `openai-whisper`: OpenAI Whisper 模型库。
    - `torch`: PyTorch，Whisper 运行所依赖的深度学习框架。
    - `ffmpeg-python`: 用于音视频处理。
    - `pysrt`: 用于处理 SRT 字幕文件。

4.  **安装 FFmpeg**:
    本工具依赖 FFmpeg 进行音视频处理。请确保你的系统已安装 FFmpeg 并将其添加到环境变量 `PATH` 中。
    - **Windows**: 可从 https://www.gyan.dev/ffmpeg/builds/ 下载完整包，解压后将 `bin` 目录添加到 `PATH`。
    - **macOS**: 可使用 Homebrew 安装: `brew install ffmpeg`
    - **Linux**: 可使用包管理器安装: `sudo apt update && sudo apt install ffmpeg` (Ubuntu/Debian) 或 `sudo yum install ffmpeg` (CentOS/RHEL)

## 使用方法

1.  **运行 GUI 程序**:
    ```bash
    python whisper_subtitle_app/gui.py
    ```

2.  **在 GUI 界面中**:
    - 点击 "添加文件" 选择一个或多个音视频文件。
    - 选择识别的语言（可选，"自动检测" 通常效果不错）。
    - 选择 Whisper 模型大小（`base` 是一个平衡的选择）。
    - 选择输出字幕文件的目录。
    - （新增）在 "最大字符数" 输入框中，可以设置单行字幕的最大字符数（英文/标点），默认为 20。设置为 0 或留空则不进行分割。
    - 点击 "开始处理"，等待处理完成。

3.  **查看结果**:
    处理完成后，生成的 `.srt` 字幕文件将保存在你指定的输出目录中。

## 注意事项

- 首次运行时，Whisper 模型会自动下载到本地缓存（通常在用户主目录下），这可能需要一些时间，取决于网络速度。
- 较大的模型（如 `large`）会更准确但速度更慢，且需要更多内存/显存。
- 如果你有 NVIDIA GPU 并安装了 CUDA，Whisper 会自动使用 GPU 加速，大大提升处理速度。