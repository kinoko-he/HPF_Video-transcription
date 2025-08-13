import os
import whisper
import ffmpeg
import datetime
import tempfile
import re
import pysrt

# 尝试导入 stable-ts 库
try:
    import stable_whisper
    STABLE_TS_AVAILABLE = True
except ImportError:
    STABLE_TS_AVAILABLE = False

# 支持的音视频文件扩展名
SUPPORTED_FORMATS = {
    'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm']
}

def get_file_type(file_path):
    """判断文件是音频还是视频"""
    _, ext = os.path.splitext(file_path)
    ext = ext[1:].lower() # 去掉点号并转为小写
    if ext in SUPPORTED_FORMATS['audio']:
        return 'audio'
    elif ext in SUPPORTED_FORMATS['video']:
        return 'video'
    else:
        return None

def extract_audio(file_path, output_audio_path):
    """
    从音视频文件中提取音频
    """
    try:
        # 使用ffmpeg-python进行音频提取
        # -y 参数表示覆盖输出文件
        # acodec: 音频编码器，这里设置为 'pcm_s16le' (WAV 16-bit) 以确保兼容性
        # ar: 音频采样率，设置为 16000Hz
        # ac: 音频通道数，设置为 1 (单声道)
        (
            ffmpeg
            .input(file_path)
            .output(output_audio_path, acodec='pcm_s16le', ar='16000', ac=1, y='-y')
            .overwrite_output()
            .run(quiet=True) # 设置quiet=True以减少输出
        )
        print(f"成功提取音频到: {output_audio_path}")
        return True
    except ffmpeg.Error as e:
        # 打印错误信息以便调试
        print(f"提取音频时出错 (ffmpeg): {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        print(f"提取音频时发生未知错误: {e}")
        return False

def seconds_to_srt_time(seconds):
    """将秒数转换为SRT时间格式 (HH:MM:SS,mmm)"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"

def generate_srt(segments, output_srt_path):
    """根据Whisper的segments生成SRT文件"""
    try:
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                start_time = seconds_to_srt_time(segment['start'])
                end_time = seconds_to_srt_time(segment['end'])
                text = segment['text'].strip()
                
                # SRT格式: 序号\n开始时间 --> 结束时间\n文本\n\n
                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        print(f"SRT字幕文件已保存至: {output_srt_path}")
        return True
    except Exception as e:
        print(f"保存SRT文件时出错: {e}")
        return False

def split_long_lines(srt_file_path, max_chars_per_line=20):
    """
    对SRT文件中的长行进行智能分割。
    
    :param srt_file_path: SRT文件路径
    :param max_chars_per_line: 每行最大字符数（英文/标点）
    :return: True if successful, False otherwise
    """
    if max_chars_per_line <= 0:
        print("最大字符数设置为0或负数，跳过字幕行分割。")
        return True
        
    try:
        # 读取SRT文件
        subs = pysrt.open(srt_file_path, encoding='utf-8')
        
        new_subs = pysrt.SubRipFile() # 创建一个新的SRT文件对象
        new_index = 1 # 新的字幕序号
        
        # 定义优先级的标点符号，用于寻找分割点
        # 逗号、顿号、分号作为首选分割点，句号、感叹号、问号作为次选
        preferred_punctuation = [',', '、', ';']
        secondary_punctuation = ['。', '！', '!', '.', '?']
        all_punctuation = preferred_punctuation + secondary_punctuation
        
        for sub in subs:
            text = sub.text.strip()
            
            # 如果文本长度小于等于最大字符数，或者没有空格和标点，则不进行分割
            if len(text) <= max_chars_per_line or not any(c in text for c in all_punctuation + [' ']):
                new_sub = pysrt.SubRipItem(index=new_index, start=sub.start, end=sub.end, text=text)
                new_subs.append(new_sub)
                new_index += 1
                continue
            
            # 需要分割
            parts = []
            remaining_text = text
            
            while len(remaining_text) > max_chars_per_line:
                # 寻找最佳分割点
                split_point = -1
                # 1. 优先在首选标点符号处分割
                for punct in preferred_punctuation:
                    # 从最大长度处向前查找
                    temp_split_point = remaining_text.rfind(punct, 0, max_chars_per_line)
                    if temp_split_point != -1:
                        split_point = temp_split_point + 1 # 包含标点符号
                        break
                
                # 2. 如果没找到首选标点，则在次选标点处分割
                if split_point == -1:
                    for punct in secondary_punctuation:
                        temp_split_point = remaining_text.rfind(punct, 0, max_chars_per_line)
                        if temp_split_point != -1:
                            split_point = temp_split_point + 1 # 包含标点符号
                            break
                
                # 3. 如果还没找到标点，则在空格处分割（避免拆分单词）
                if split_point == -1:
                    # 从最大长度处向前查找最近的空格
                    split_point = remaining_text.rfind(' ', 0, max_chars_per_line)
                    if split_point != -1:
                        split_point += 1 # 空格后开始新行
                
                # 4. 如果连空格都没找到，就强制在max_chars_per_line处分割（不太理想，但避免无限循环）
                if split_point <= 0 or split_point >= len(remaining_text):
                    split_point = max_chars_per_line
                
                # 分割文本
                part = remaining_text[:split_point].strip()
                parts.append(part)
                remaining_text = remaining_text[split_point:].strip()
            
            # 添加最后一部分（如果有的话）
            if remaining_text:
                parts.append(remaining_text)
            
            # 如果只分割成一部分，则无需改变时间戳
            if len(parts) == 1:
                new_sub = pysrt.SubRipItem(index=new_index, start=sub.start, end=sub.end, text=parts[0])
                new_subs.append(new_sub)
                new_index += 1
            else:
                # 计算总时长（秒）
                total_duration = (sub.end.ordinal - sub.start.ordinal) / 1000.0 # pysrt时间戳是毫秒
                
                # 按字符长度分配时间
                total_chars = sum(len(part) for part in parts)
                if total_chars == 0: 
                    total_chars = 1 # 避免除以零
                
                current_start_time = sub.start
                
                for i, part in enumerate(parts):
                    # 计算当前片段的持续时间
                    part_duration = total_duration * (len(part) / total_chars)
                    
                    # 确保至少有最小显示时间，例如0.5秒
                    min_duration = 0.5
                    if part_duration < min_duration and i < len(parts) - 1:
                        part_duration = min_duration
                    
                    # 计算结束时间
                    current_end_time = pysrt.SubRipTime.from_ordinal(int(current_start_time.ordinal + part_duration * 1000))
                    
                    # 确保结束时间不超过原字幕的结束时间
                    if i == len(parts) - 1: # 最后一部分
                        current_end_time = sub.end
                    
                    # 创建新的字幕项
                    new_sub = pysrt.SubRipItem(index=new_index, start=current_start_time, end=current_end_time, text=part)
                    new_subs.append(new_sub)
                    new_index += 1
                    
                    # 下一个片段的开始时间是当前片段的结束时间
                    current_start_time = current_end_time

        # 保存修改后的SRT文件
        new_subs.save(srt_file_path, encoding='utf-8')
        print(f"字幕行分割完成并保存至: {srt_file_path}")
        return True
        
    except Exception as e:
        print(f"分割SRT文件时出错: {e}")
        return False

def transcribe_audio(audio_path, language=None, model_size='base'):
    """
    使用Whisper模型对音频进行转录
    :param audio_path: 音频文件路径
    :param language: 音频语言 (可选, 如 'zh', 'en')
    :param model_size: Whisper模型大小 ('tiny', 'base', 'small', 'medium', 'large')
    :return: 转录结果 (包含segments的字典) 或 None
    """
    try:
        print(f"正在加载Whisper {model_size} 模型...")
        # 尝试加载模型到GPU (如果可用)
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"正在使用 {device.upper()} 进行推理...")
        
        # 根据是否安装了 stable-ts 选择使用哪种方法
        if STABLE_TS_AVAILABLE:
            print("检测到 stable-ts，将使用优化的时间戳...")
            model = stable_whisper.load_model(model_size, device=device)
            using_stable_ts = True
        else:
            print("未检测到 stable-ts，将使用原始Whisper...")
            model = whisper.load_model(model_size, device=device)
            using_stable_ts = False
        print("模型加载完成。")

        # 准备转录选项
        transcribe_options = {
            "task": "transcribe",
            "verbose": False, # 不在控制台打印详细信息
        }
        
        # 如果是CPU或用户明确要求，或者在CPU上fp16导致问题，则禁用fp16
        # 在GPU (CUDA) 上，默认可以使用fp16以提高性能
        if device == "cpu":
            transcribe_options["fp16"] = False 
        else:
            # 在GPU上，可以尝试启用fp16以提高性能，除非遇到兼容性问题
            # whisper库通常能很好地处理这一点，所以我们可以不显式设置
            pass
            
        # 如果指定了语言，则添加到选项中
        if language:
            transcribe_options["language"] = language
            
        # 显示使用的转录方法
        method = "stable-ts优化版" if using_stable_ts else "原始Whisper"
        print(f"正在使用 {method} 进行语音识别 (语言: {language or 'auto-detect'}, 设备: {device.upper()}, 模型: {model_size})...")
        
        # 根据是否安装了 stable-ts 选择使用哪种转录方法
        if using_stable_ts:
            # 为 stable-ts 添加更多参数以提高时间轴准确性
            transcribe_options.update({
                "suppress_silence": True,  # 抑制静默段落
                "suppress_word_ts": False,  # 不抑制单词级时间戳
                "gap_padding": "pad",  # 间隙填充方式
                "only_voice_freq": False,  # 仅保留语音频率
                "vad": True,  # 使用语音活动检测
            })
            print(f"stable-ts 参数: {transcribe_options}")
            result = model.transcribe(audio_path, **transcribe_options)
            # stable-ts 返回的结果需要转换为字典格式
            result = result.to_dict()
        else:
            result = model.transcribe(audio_path, **transcribe_options)
            
        print(f"语音识别完成。使用的转录方法: {method}")
        return result
    except Exception as e:
        print(f"语音识别时出错: {e}")
        return None

def process_file(input_file_path, output_dir, language=None, model_size='base', max_chars=20):
    """
    处理单个文件（音视频）并生成SRT字幕
    :param input_file_path: 输入文件路径
    :param output_dir: 输出SRT文件的目录
    :param language: 音频语言 (可选)
    :param model_size: Whisper模型大小
    :param max_chars: 每行最大字符数 (0表示不启用分割)
    :return: True if successful, False otherwise
    """
    file_type = get_file_type(input_file_path)
    if not file_type:
        print(f"不支持的文件格式: {input_file_path}")
        return False

    # 获取不带扩展名的文件名
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_srt_path = os.path.join(output_dir, f"{base_name}.srt")

    audio_path_to_transcribe = input_file_path # 默认直接使用输入文件（如果是音频）
    
    # 如果是视频文件，需要先提取音频
    if file_type == 'video':
        print(f"检测到视频文件: {input_file_path}")
        # 创建临时文件来存储提取的音频
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio_file:
            tmp_audio_path = tmp_audio_file.name
            
        if not extract_audio(input_file_path, tmp_audio_path):
            print("提取音频失败。")
            # 清理临时文件
            if os.path.exists(tmp_audio_path):
                os.remove(tmp_audio_path)
            return False
        
        audio_path_to_transcribe = tmp_audio_path
        print(f"音频提取成功: {audio_path_to_transcribe}")

    # 进行语音识别
    result = transcribe_audio(audio_path_to_transcribe, language=language, model_size=model_size)
    
    # 如果是视频文件，清理临时音频文件
    if file_type == 'video' and 'tmp_audio_path' in locals():
        if os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)
        print("临时音频文件已清理。")
        
    if result and 'segments' in result:
        # 生成SRT文件
        if generate_srt(result['segments'], output_srt_path):
            print(f"成功为 {input_file_path} 生成字幕文件 {output_srt_path}")
            # 新增：如果设置了最大字符数，则对生成的SRT文件进行分割
            if max_chars > 0:
                print(f"正在对字幕文件进行行分割，最大字符数: {max_chars}")
                if split_long_lines(output_srt_path, max_chars_per_line=max_chars):
                    print(f"字幕行分割完成: {output_srt_path}")
                else:
                    print(f"字幕行分割失败: {output_srt_path}")
                    return False
            return True
        else:
            print(f"为 {input_file_path} 生成SRT文件失败。")
            return False
    else:
        print(f"语音识别未返回有效结果: {input_file_path}")
        return False

# --- 以下为测试和演示用途 ---
if __name__ == '__main__':
    # 这里可以添加一些简单的测试代码
    # 例如: process_file('test.mp4', './output', language='zh')
    pass