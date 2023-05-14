import os
from pathlib import Path

# 创建一个Path对象
current_file_path = Path(__file__)
# 获取当前文件所在的目录上上级目录
current_dir_path = current_file_path.parent.parent

RESOURCE_BASE_PATH = current_dir_path / 'resources' / 'LittlePaimon'


# 字体路径
FONTS_PATH = current_dir_path / 'resources' / 'fonts'



