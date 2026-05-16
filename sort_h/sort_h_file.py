#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# C 头文件排序工具 —— 将 #include, #define, const int 等按规范顺序重排
# python sort_h_file.py original.h sorted.h

import re
import sys


def sort_h_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. 分离头部预处理保护（#ifdef, #ifndef, #define 等连续块）
    preprocessor_guard = []
    remaining_lines = []
    guard_pattern = re.compile(r'^#\s*(ifdef|ifndef|define|endif|elif|else)\b')
    in_guard = True
    for line in lines:
        if in_guard and guard_pattern.match(line.strip()):
            preprocessor_guard.append(line)
        else:
            in_guard = False
            remaining_lines.append(line)

    # 2. 从剩余内容中分离 #include
    includes = []
    content_lines = []
    include_pattern = re.compile(r'^#\s*include\b')
    for line in remaining_lines:
        if include_pattern.match(line.strip()):
            includes.append(line)
        else:
            content_lines.append(line)

    # 3. 分离 #define, const int 和其他
    defines = []
    consts = []
    others = []
    define_pattern = re.compile(r'^#\s*define\b')
    const_pattern = re.compile(r'^const\s+int\b')
    for line in content_lines:
        stripped = line.strip()
        if not stripped:
            others.append(line)
        elif define_pattern.match(stripped):
            defines.append(line)
        elif const_pattern.match(stripped):
            consts.append(line)
        else:
            others.append(line)

    # 4. 按序组合：保护 → include → define → 其他 → const int
    new_lines = list(preprocessor_guard)
    if includes:
        new_lines.append('\n')
        new_lines.extend(includes)
    if defines:
        new_lines.append('\n')
        new_lines.extend(defines)
    if others:
        new_lines.append('\n')
        new_lines.extend(others)
    if consts:
        new_lines.append('\n')
        new_lines.extend(consts)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sort_h_file.py <input.h> <output.h>")
        exit(1)
    sort_h_file(sys.argv[1], sys.argv[2])
    print(f"处理完成: {sys.argv[1]} -> {sys.argv[2]}")
