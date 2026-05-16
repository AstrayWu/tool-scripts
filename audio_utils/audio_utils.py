#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 音频处理工具库 —— 32位PCM格式转换、噪声生成/添加、声道混合
# Dependencies: numpy, soundfile, scipy

import os
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, resample


# ------------------------------
# 1. 基础音频读写与格式转换
# ------------------------------
def read_audio(file_path, target_sr=48000):
    """读取WAV或PCM文件，返回 (audio_data, sample_rate)，数据为 float32 [-1,1]"""
    try:
        data, sr = sf.read(file_path)
    except:
        data, sr = sf.read(
            file_path, samplerate=target_sr, subtype='PCM_32',
            format='RAW', channels=1
        )
    if len(data.shape) > 1 and data.shape[1] > 1:
        data = np.mean(data, axis=1)
    if data.dtype.kind not in 'f':
        data = data.astype(np.float32) / np.iinfo(data.dtype).max
    return data.astype(np.float32), sr


def write_pcm_32bit(file_path, data, sample_rate=48000):
    """写入32位PCM文件"""
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    sf.write(file_path, data, samplerate=sample_rate, format='RAW', subtype='PCM_32')


def convert_to_32bit_pcm(input_path, output_path, target_sr=48000):
    """单个文件转48K 32位PCM，返回 (success, message)"""
    try:
        data, sr = read_audio(input_path, target_sr)
        if sr != target_sr:
            data = resample(data, int(len(data) * target_sr / sr))
            sr = target_sr
        data = np.clip(data, -1.0, 1.0)
        write_pcm_32bit(output_path, data, sr)
        return True, f"转换成功: {os.path.basename(input_path)}"
    except Exception as e:
        return False, f"转换失败: {str(e)}"


def batch_convert_to_32bit_pcm(input_dir, output_dir, target_sr=48000):
    """批量转换文件夹中音频为32位PCM，返回 (success_count, failed_files)"""
    os.makedirs(output_dir, exist_ok=True)
    total = 0
    success_count = 0
    failed_files = []
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if not os.path.isfile(input_path):
            continue
        total += 1
        pcm_filename = os.path.splitext(filename)[0] + ".pcm"
        output_path = os.path.join(output_dir, pcm_filename)
        success, msg = convert_to_32bit_pcm(input_path, output_path, target_sr)
        print(msg)
        if success:
            success_count += 1
        else:
            failed_files.append(filename)
    print(f"\n批量转换完成: 总{total}，成功{success_count}，失败{len(failed_files)}")
    return success_count, failed_files


# ------------------------------
# 2. 噪声生成与添加
# ------------------------------
def _butter_filter(data, cutoff, fs, btype='low', order=5):
    """内部巴特沃斯滤波器"""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return lfilter(b, a, data)


def generate_noise(length, noise_type, sample_rate=48000):
    """生成指定类型噪声: 'white', 'pink', 'brown'"""
    noise = np.random.normal(0, 1, length).astype(np.float32)
    if noise_type == 'white':
        return noise
    elif noise_type == 'pink':
        noise = _butter_filter(noise, 1000, sample_rate, 'high', 2)
        noise = _butter_filter(noise, 1000, sample_rate, 'low', 2)
        return (noise - np.mean(noise)) / np.std(noise)
    elif noise_type == 'brown':
        noise = np.cumsum(noise)
        noise = _butter_filter(noise, 50, sample_rate, 'high', 3)
        segment_len = sample_rate
        for i in range(0, length, segment_len):
            end = min(i + segment_len, length)
            segment = noise[i:end]
            segment = (segment - np.mean(segment)) / (np.std(segment) + 1e-10)
            noise[i:end] = segment
        return (noise - np.mean(noise)) / np.std(noise)
    else:
        raise ValueError(f"不支持的噪声类型: {noise_type}")


def add_noise(input_path, output_path, noise_type='white',
              signal_gain=1.0, noise_amplitude=0.1, target_sr=48000):
    """给音频添加噪声并输出32位PCM"""
    audio_data, sr = read_audio(input_path, target_sr)
    if sr != target_sr:
        audio_data = resample(audio_data, int(len(audio_data) * target_sr / sr))
        sr = target_sr
    audio_data *= signal_gain
    noise = generate_noise(len(audio_data), noise_type, sr)
    noise *= noise_amplitude
    mixed = np.clip(audio_data + noise, -1.0, 1.0)
    write_pcm_32bit(output_path, mixed, sr)
    print(f"已添加{noise_type}噪声: {output_path}")


# ------------------------------
# 3. 声道混合（矩阵实现）
# ------------------------------
def channel_mixing(audio_data, mix_matrix):
    """矩阵运算实现声道混合，mix_matrix 形状: [输出声道数, 输入声道数]"""
    if len(audio_data.shape) == 1:
        audio_data = audio_data.reshape(-1, 1)
    input_ch = audio_data.shape[1]
    output_ch, mix_input_ch = mix_matrix.shape
    if input_ch != mix_input_ch:
        raise ValueError(f"声道数不匹配: 输入{input_ch} vs 矩阵{mix_input_ch}")
    return np.dot(audio_data, mix_matrix.T)


# ------------------------------
# 4. PCM时长计算
# ------------------------------
def calculate_pcm_duration(file_path, sample_rate=48000, bit_depth=32, channels=1):
    """计算PCM文件时长（秒）"""
    file_size = os.path.getsize(file_path)
    bytes_per_sec = sample_rate * (bit_depth // 8) * channels
    return file_size / bytes_per_sec if bytes_per_sec != 0 else 0.0
