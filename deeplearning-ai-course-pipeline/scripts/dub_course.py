#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepLearning.AI 课程视频中文口播配音与音视频封装脚本
- 采用微软 Edge Neural 神经网络语音 (默认 03 云哲 zh-TW-YunJheNeural)
- 智能语义连贯合并短句，确保自然语调
- 专有技术术语与人名发音映射词典
- 弹性时间轴对齐 (1.00x ~ 1.28x)
- FFmpeg 无损拷贝画面 + 双音轨 (中文默认 / 英文保留) + 双语内嵌字幕
"""

import os
import sys
import re
import json
import asyncio
import argparse
import subprocess
import tempfile
import shutil
import wave

DEFAULT_VOICE = "zh-TW-YunJheNeural"
DEFAULT_RATE = "+10%"
SAMPLE_RATE = 48000
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

def clean_text_for_tts(t: str) -> str:
    """清理屏幕注记、生僻姓名与技术术语发音校正"""
    t = re.sub(r'<[^>]+>', '', t)
    
    # 1. 讲师与人名自然化
    t = t.replace('Elie Schoppik', 'Elie')
    t = t.replace('谢谢 Andrew。我非常高兴能与你一起讲授这门课程。', '谢谢吴恩达老师，很高兴能与你一起讲授这门课程。')
    t = t.replace('谢谢 Andrew。', '谢谢吴恩达老师，')
    t = t.replace('谢谢 Andrew，', '谢谢吴恩达老师，')
    t = t.replace('Hawraa Salami', 'Hawraa')
    
    # 2. 剥离仅供屏幕视觉参考的英文括号注释
    t = t.replace('（Model Context Protocol，简称 MCP）', '，即 MCP，')
    t = t.replace('（Head of Technical Education）', '')
    t = t.replace('（Specification）', '')
    t = t.replace('（Model Agnostic）', '')
    t = t.replace('（Research Assistant Agent）', '')
    t = t.replace('（MCP）', ' MCP ')
    t = t.replace('（LLM）', ' LLM ')
    t = re.sub(r'（.*?）', '', t)
    t = re.sub(r'\(.*?\)', '', t)
    
    # 3. 专有名词与技术术语发音优化
    t = t.replace('Claude Desktop', 'Claude 桌面端')
    t = t.replace('大语言模型（LLM）', '大语言模型 LLM ')
    t = t.replace('大语言模型 LLM', '大模型 LLM')
    t = t.replace('《', '').replace('》', '')
    t = t.replace('：', '，')
    
    # 清理多余空格
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def parse_and_merge_srt(path: str):
    """解析 SRT 字幕，并智能合并相邻且语法未完结的短句片段"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    entries = []
    blocks = content.split('\n\n')
    for b in blocks:
        lines = b.strip().split('\n')
        if len(lines) >= 3:
            idx = int(lines[0].strip())
            times = lines[1].strip()
            text = ' '.join(lines[2:]).strip()
            m = re.match(r'(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)', times)
            if m:
                s_h, s_m, s_s, s_ms = map(int, m.groups()[:4])
                e_h, e_m, e_s, e_ms = map(int, m.groups()[4:])
                start = s_h * 3600 + s_m * 60 + s_s + s_ms / 1000.0
                end = e_h * 3600 + e_m * 60 + e_s + e_ms / 1000.0
                entries.append({'id': idx, 'start': start, 'end': end, 'dur': end - start, 'text': text})

    merged = []
    curr = None
    for e in entries:
        if curr is None:
            curr = dict(e)
            curr['merged_ids'] = [e['id']]
        else:
            gap = e['start'] - curr['end']
            prev_text = curr['text'].strip()
            ends_sentence = prev_text.endswith('。') or prev_text.endswith('！') or prev_text.endswith('？')
            if gap < 0.25 and not ends_sentence:
                curr['end'] = e['end']
                curr['dur'] = curr['end'] - curr['start']
                curr['text'] = prev_text + ' ' + e['text']
                curr['merged_ids'].append(e['id'])
            else:
                merged.append(curr)
                curr = dict(e)
                curr['merged_ids'] = [e['id']]
    if curr:
        merged.append(curr)

    for m in merged:
        m['clean_text'] = clean_text_for_tts(m['text'])
    return merged

def get_audio_duration(path: str) -> float:
    cmd = [FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(res.stdout)['format']['duration'])

def convert_and_adjust_audio(src_mp3: str, dst_wav: str, speed: float):
    if abs(speed - 1.0) < 0.01:
        cmd = [FFMPEG, '-y', '-i', src_mp3, '-ar', str(SAMPLE_RATE), '-ac', '2', '-c:a', 'pcm_s16le', dst_wav]
    else:
        cmd = [FFMPEG, '-y', '-i', src_mp3, '-filter:a', f'atempo={speed:.4f}', '-ar', str(SAMPLE_RATE), '-ac', '2', '-c:a', 'pcm_s16le', dst_wav]
    subprocess.run(cmd, capture_output=True, check=True)

async def dub_lesson(lesson_dir: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE):
    import edge_tts
    folder_name = os.path.basename(lesson_dir.rstrip('/'))
    mp4_files = [f for f in os.listdir(lesson_dir) if f.endswith('.mp4') and not f.endswith('_zh.mp4')]
    if not mp4_files:
        print(f"[{folder_name}] 未找到源视频 MP4 文件，跳过。")
        return
    
    video_path = os.path.join(lesson_dir, mp4_files[0])
    base_name = mp4_files[0][:-4]
    srt_path = os.path.join(lesson_dir, f"{base_name}.zh.srt")
    if not os.path.exists(srt_path):
        srt_path = os.path.join(lesson_dir, f"{folder_name}.zh.srt")
    if not os.path.exists(srt_path):
        print(f"[{folder_name}] 未找到中文字幕文件: {srt_path}，跳过。")
        return

    bilingual_srt = os.path.join(lesson_dir, f"{base_name}.zh_en.srt")
    if not os.path.exists(bilingual_srt):
        bilingual_srt = os.path.join(lesson_dir, f"{folder_name}.zh_en.srt")
    if not os.path.exists(bilingual_srt):
        bilingual_srt = srt_path

    output_video = os.path.join(lesson_dir, f"{base_name}_zh.mp4")
    print(f"\n==========================================")
    print(f"开始处理: {folder_name}")
    print(f"采用音色: {voice} | 基础语速: {rate}")
    print(f"输入视频: {video_path}")
    print(f"输出视频: {output_video}")
    print(f"==========================================")

    video_dur = get_audio_duration(video_path)
    segments = parse_and_merge_srt(srt_path)
    print(f"语义合并为 {len(segments)} 个自然语音句段，视频总时长: {video_dur:.2f}s")

    temp_dir = tempfile.mkdtemp(prefix=f"dub_{folder_name}_")
    try:
        sem = asyncio.Semaphore(10)
        async def synth_segment(i, seg):
            async with sem:
                mp3_p = os.path.join(temp_dir, f"seg_{i:03d}.mp3")
                comm = edge_tts.Communicate(seg['clean_text'], voice, rate=rate)
                await comm.save(mp3_p)
                seg['mp3'] = mp3_p

        print("正在调用 Edge Neural 神经网络批量合成中文语音...")
        await asyncio.gather(*[synth_segment(i, s) for i, s in enumerate(segments)])

        for seg in segments:
            seg['raw_dur'] = get_audio_duration(seg['mp3'])

        total_samples = int(round(video_dur * SAMPLE_RATE))
        audio_buffer = bytearray(total_samples * 4)

        current_time = 0.0
        for i, seg in enumerate(segments):
            start_target = seg['start']
            actual_start = max(start_target, current_time)

            if i + 1 < len(segments):
                avail_dur = segments[i+1]['start'] - actual_start
            else:
                avail_dur = video_dur - actual_start

            raw_dur = seg['raw_dur']
            if raw_dur > avail_dur - 0.05 and avail_dur > 0.1:
                speed = raw_dur / (avail_dur - 0.05)
                speed = min(speed, 1.28)
            else:
                speed = 1.0

            wav_path = os.path.join(temp_dir, f"seg_{i:03d}.wav")
            convert_and_adjust_audio(seg['mp3'], wav_path, speed)
            actual_dur = get_audio_duration(wav_path)

            with wave.open(wav_path, 'rb') as wf:
                pcm_data = wf.readframes(wf.getnframes())

            start_sample = int(round(actual_start * SAMPLE_RATE))
            start_byte = start_sample * 4
            end_byte = start_byte + len(pcm_data)

            if end_byte > len(audio_buffer):
                pcm_data = pcm_data[:len(audio_buffer) - start_byte]
                end_byte = len(audio_buffer)

            audio_buffer[start_byte:end_byte] = pcm_data
            current_time = actual_start + actual_dur + 0.05

        full_wav_path = os.path.join(temp_dir, "chinese_full.wav")
        with wave.open(full_wav_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_buffer)

        print("中文音轨时间轴对齐组装完成，正在封装 MP4 容器...")
        mux_cmd = [
            FFMPEG, '-y',
            '-i', video_path,
            '-i', full_wav_path,
            '-i', bilingual_srt,
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-map', '0:a:0',
            '-map', '2:s:0',
            '-c:v', 'copy',
            '-c:a:0', 'aac', '-b:a:0', '192k', '-metadata:s:a:0', f'title=中文口播', '-metadata:s:a:0', 'language=chi',
            '-c:a:1', 'copy', '-metadata:s:a:1', 'title=English (Original)', '-metadata:s:a:1', 'language=eng',
            '-c:s', 'mov_text', '-metadata:s:s:0', 'title=中英双语字幕', '-metadata:s:s:0', 'language=chi',
            '-disposition:a:0', 'default',
            '-disposition:a:1', '0',
            '-disposition:s:0', 'default',
            output_video
        ]
        res = subprocess.run(mux_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"封装错误: {res.stderr}")
            return
        
        size_mb = os.path.getsize(output_video) / (1024 * 1024)
        print(f"[OK] 处理完成! 生成双音轨视频: {output_video} ({size_mb:.1f} MB)")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def main():
    parser = argparse.ArgumentParser(description="DeepLearning.AI 课程视频中文口播生成器")
    parser.add_argument("--course-dir", type=str, default=".", help="课程根目录，默认当前目录")
    parser.add_argument("--lesson", type=str, default=None, help="指定章节目录名，例如 01_introduction 或 01")
    parser.add_argument("--all", action="store_true", help="批量处理课程下所有章节")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help=f"TTS 音色，默认 {DEFAULT_VOICE}")
    parser.add_argument("--rate", type=str, default=DEFAULT_RATE, help="TTS 基础语速，默认 +10%")
    args = parser.parse_args()

    course_root = os.path.abspath(args.course_dir)
    subdirs = sorted([
        os.path.join(course_root, d) for d in os.listdir(course_root)
        if os.path.isdir(os.path.join(course_root, d)) and not d.startswith('.') and d != '__pycache__' and d != 'voice_samples'
    ])

    if args.lesson:
        target_dirs = [d for d in subdirs if args.lesson in os.path.basename(d)]
        if not target_dirs:
            print(f"未找到匹配的章节目录: {args.lesson}")
            return
        for d in target_dirs:
            await dub_lesson(d, voice=args.voice, rate=args.rate)
    elif args.all:
        for d in subdirs:
            await dub_lesson(d, voice=args.voice, rate=args.rate)
    else:
        print("请指定 --lesson <章节> 或 --all")

if __name__ == '__main__':
    asyncio.run(main())
