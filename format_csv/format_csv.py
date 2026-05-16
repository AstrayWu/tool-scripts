#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 2019.4.26 by astraywu
# 给组里使用的CSV文件进行格式化
# python format_csv.py test.csv output.csv

import sys
import csv

COLS = 11  # 期望的列数


def getlen(data):
    """获取字符串在等宽字体下的显示宽度，中文按2，英文按1"""
    count = len(data)
    for s in data:
        if ord(s) > 127:
            count += 1
    return count


def getchineselen(data):
    """获取中文字符的个数"""
    count = 0
    for s in data:
        if ord(s) > 127:
            count += 1
    return count


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_csv.py <input.csv> <output.csv>")
        exit(1)
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]

    with open(in_filename, 'r', encoding='utf-8', newline='') as fin:
        reader = csv.reader(fin)
        all_rows = []
        data_rows = []  # 需要格式化的数据行（剥离首列后的部分）
        f0 = []  # 首列等号左边的变量名
        f1 = []  # 首列等号右边的值

        for row in reader:
            all_rows.append(row)
            if len(row) != COLS or row[0].startswith('#') or '#' not in row[0]:
                continue
            f0.append(row[0].split('=')[0].strip())
            f1.append(row[0].split('=')[1].strip('# '))
            data_rows.append([item.strip() for item in row])

        widths = [max(getlen(row[i]) for row in data_rows) for i in range(len(data_rows[0]))]
        w0 = max(len(row) for row in f0)
        w1 = max(len(row) for row in f1)

    with open(out_filename, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.writer(fout)
        for row in all_rows:
            if len(row) != COLS or row[0].startswith('#') or '#' not in row[0]:
                writer.writerow(row)
                continue

            f00 = row[0].split('=')[0].strip()
            f11 = row[0].split('=')[1].strip('# ')
            row = [item.strip() for item in row]

            row_formatted = [f00.ljust(w0) + ' = ' + f11.ljust(w1) + ' #']
            for i in range(1, len(row)):
                # 中文字符用空格补齐到宽度（中文已在 getlen 中计为2）
                item = row[i].ljust(widths[i], '#')
                row_formatted.append(item.ljust(widths[i] - getchineselen(item), ' '))
            writer.writerow(row_formatted)
