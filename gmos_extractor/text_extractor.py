#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# G-MOS 版本号提取器 —— 从文本中提取 TS 103 106 标准的版本号
# 作为模块导入使用：from gmos_extractor.text_extractor import GMOSVersionExtractor

import re
from typing import List


class GMOSVersionExtractor:
    """提取两种 G-MOS 格式的版本号：
    1. G-MOS (TS 103 106) 4.1
    2. G-MOS (Average, TS 103 106): 4.2
    """

    def __init__(self):
        self.pattern_basic = re.compile(
            r'^G-MOS \(TS 103 106\)\s+(\d+\.\d+)\s*$',
            re.MULTILINE
        )
        self.pattern_with_average = re.compile(
            r'^G-MOS \(Average, TS 103 106\):\s*(\d+\.\d+)',
            re.MULTILINE
        )

    def extract_all(self, text: str) -> List[str]:
        """提取所有版本号，去重保持顺序"""
        basic = self.pattern_basic.findall(text)
        avg = self.pattern_with_average.findall(text)
        seen = set()
        result = []
        for v in basic + avg:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result

    def extract_basic(self, text: str) -> List[str]:
        return self.pattern_basic.findall(text)

    def extract_with_average(self, text: str) -> List[str]:
        return self.pattern_with_average.findall(text)
