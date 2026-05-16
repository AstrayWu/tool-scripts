#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 音频问题检测 —— 扫描目录识别全零/低能量音频文件
# Dependencies: librosa

import os
import sys
import librosa


def load_audio(file_path):
    """使用librosa加载音频文件，返回 (data, sample_rate)"""
    try:
        y, sr = librosa.load(file_path, sr=None)
        return y, sr
    except Exception as e:
        print(f"警告：无法加载 {os.path.basename(file_path)} - {str(e)}")
        return None, None


def is_all_zero_audio(y):
    """检查音频是否全为零"""
    return (y == 0).all()


def calculate_average_energy(y):
    """计算音频的平均能量"""
    if len(y) == 0:
        return 0.0
    return (y ** 2).mean()


def check_audio_files(root_dir, mode='both', energy_threshold=100.0):
    """遍历目录检测音频问题
    mode: 'zero' | 'low_energy' | 'both'
    """
    print(f"开始检查目录: {root_dir}")
    print(f"检测模式: {mode}，能量阈值: {energy_threshold}")
    print("-" * 70)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(('.wav', '.mp3', '.flac')):
                file_path = os.path.join(dirpath, filename)
                y, _ = load_audio(file_path)
                if y is None:
                    continue
                if mode in ('zero', 'both') and is_all_zero_audio(y):
                    print(f"全零音频: {file_path}")
                    if mode == 'zero':
                        continue
                if mode in ('low_energy', 'both'):
                    avg_energy = calculate_average_energy(y)
                    if avg_energy < energy_threshold:
                        print(f"低能量音频: {file_path}（平均能量: {avg_energy:.6f}）")

    print("-" * 70)
    print("检查完成")


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3, 4]:
        print("用法:")
        print("  检查全零音频:     python check_audio_issues.py <目录> zero")
        print("  检查低能量音频:   python check_audio_issues.py <目录> low_energy [阈值]")
        print("  检查两者:         python check_audio_issues.py <目录> both [阈值]")
        sys.exit(1)

    target_dir = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) >= 3 else 'both'
    energy_threshold = float(sys.argv[3]) if len(sys.argv) == 4 else 100.0

    if not os.path.isdir(target_dir):
        print(f"错误: {target_dir} 不是有效的目录")
        sys.exit(1)
    if mode not in ('zero', 'low_energy', 'both'):
        print(f"错误: 模式 {mode} 不支持，可选: zero, low_energy, both")
        sys.exit(1)

    check_audio_files(target_dir, mode, energy_threshold)
