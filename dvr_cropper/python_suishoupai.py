#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 行车记录仪随手拍工具 —— OCR 提取 GPS → 归档 → 生成 ffmpeg 裁剪脚本
# Dependencies: opencv-python, easyocr
# Usage: python python_suishoupai.py <视频目录> [文件匹配模式]

import re
import shutil
import logging
import sys
from pathlib import Path
from typing import Generator, Tuple, Optional
import cv2
import easyocr

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoProcessor:
    def __init__(self, ocr_languages: list = ["ch_sim", "en"], gpu: bool = True):
        self.reader = easyocr.Reader(ocr_languages, gpu=gpu)

    def extract_info(
        self,
        video_path: Path,
        crop_coords: Tuple[int, int, int, int] = (2030, 2140, 2940, 3800),
    ) -> Tuple[str, Optional[Tuple[str, str]]]:
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        basename = video_path.stem
        file_date = basename[2:15]

        vidcap = cv2.VideoCapture(str(video_path))
        success, img = vidcap.read()
        vidcap.release()
        if not success:
            raise RuntimeError(f"无法读取视频帧: {video_path}")

        y_start, y_end, x_start, x_end = crop_coords
        crop_img = img[y_start:y_end, x_start:x_end]
        gps = self._extract_gps_from_image(crop_img)
        return file_date, gps

    def _extract_gps_from_image(self, image) -> Optional[Tuple[str, str]]:
        try:
            ocr_results = self.reader.readtext(image, detail=0)
            if not ocr_results:
                return None
            ocr_text = "".join(ocr_results)
            results = re.findall(r"-?\d+\.\d+", ocr_text)
            if len(results) >= 2:
                return results[0], results[1]
            return None
        except Exception as e:
            logging.error(f"OCR 解析失败: {e}")
            return None


def gen_find_cur(
    filepat: str = "*.MP4", top: str = "./"
) -> Generator[Tuple[str, Path], None, None]:
    top_path = Path(top).resolve()
    for item in top_path.glob(filepat):
        if item.is_file():
            yield item.name, item


def main_proc(search_dir: str, filepat: str = "*.MP4"):
    script_dir = Path(__file__).parent
    crop_bat_template = script_dir / "crop.bat"

    if not crop_bat_template.exists():
        logging.error(f"crop.bat 模板未找到: {crop_bat_template}")
        sys.exit(1)

    processor = VideoProcessor()
    for file, full_path in gen_find_cur(filepat=filepat, top=search_dir):
        try:
            file_date, gps = processor.extract_info(full_path)
            logging.info(f"处理文件: {file}, 日期: {file_date}, GPS: {gps}")

            new_dir = full_path.parent / file_date
            new_dir.mkdir(exist_ok=True)

            new_path = new_dir / file
            shutil.move(str(full_path), str(new_path))

            if gps:
                txt_file_name = new_dir / "readme.txt"
                with open(txt_file_name, "w", encoding="utf-8") as fout:
                    fout.write(".".join(gps))

            target_shell_path = new_dir / "crop.bat"
            shutil.copy(str(crop_bat_template), str(target_shell_path))

            with open(target_shell_path, "r", encoding="utf-8") as fin:
                data = fin.read()
            data = data.replace("NO20240925-082139-000628F", file)
            with open(target_shell_path, "w", encoding="utf-8") as fout:
                fout.write(data)

        except Exception as e:
            logging.error(f"处理文件失败: {file} ({e})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python python_suishoupai.py <视频目录> [文件匹配模式]")
        print("Example: python python_suishoupai.py /dvr/20250127 '*.MP4'")
        sys.exit(1)

    search_dir = sys.argv[1]
    filepat = sys.argv[2] if len(sys.argv) >= 3 else "*.MP4"
    main_proc(search_dir, filepat)
