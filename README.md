# 实用工具脚本集

工作中陆续写的几个 Python 工具，合并在一起便于维护。

## 工具列表

### format_csv — CSV 配置表列对齐

对 CSV 格式的寄存器配置表按列对齐，正确处理等宽字体下中文占 2 字符宽度。

```bash
python format_csv/format_csv.py test.csv output.csv
```

### sort_h — C 头文件排序

将头文件内容按规范顺序重排：预处理保护 → `#include` → `#define` → 其他内容 → `const int`。

```bash
python sort_h/sort_h_file.py original.h sorted.h
```

### gmos_extractor — G-MOS 版本号提取

从文本中提取 G-MOS (TS 103 106) 标准的版本号。无 CLI，作为模块导入使用。

```python
from gmos_extractor.text_extractor import GMOSVersionExtractor
extractor = GMOSVersionExtractor()
versions = extractor.extract_all(text)
```

### audio_utils — 音频处理库

32位 PCM 音频处理：格式转换（WAV ↔ PCM）、噪声生成/添加（白/粉/棕）、声道矩阵混合、PCM 时长计算。

依赖：`numpy soundfile scipy`

```python
from audio_utils.audio_utils import convert_to_32bit_pcm, add_noise
```

### check_audio_issues — 音频质量检测

递归扫描目录检测全零（静音）和低能量音频文件。支持 WAV/MP3/FLAC。

依赖：`librosa`

```bash
python audio_utils/check_audio_issues.py ./audio both 50.0
```
