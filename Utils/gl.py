# coding: utf-8
"""
全局变量模块
"""

from __future__ import unicode_literals
import os

# 当前时间
TIME_NOW = None

# 当前工作目录
CWD = None

# 位图目录
BITMAP_DIR = 'bitmaps/'

# 数据目录
DATA_DIR = 'data/'

# 字体目录
FONT_DIR = 'data/font/'

# 停用词目录
STOPWORDS_DIR = 'data/stopwords/'

# 缓存目录
CACHE_DIR = 'data/.catch/'

# 主题设置
THEME = 'light'

# 版本信息
VERSION = '2.0.0'
APP_NAME = 'WordCloud GUI'

# 支持的文件格式
SUPPORTED_IMPORT_FORMATS = [
    ('TXT文件', '*.txt'),
    ('CSV文件', '*.csv'),
    ('Excel文件', '*.xlsx;*.xls'),
    ('所有文件', '*.*')
]

SUPPORTED_EXPORT_FORMATS = [
    ('PNG图片', '*.png'),
    ('JPEG图片', '*.jpg;*.jpeg'),
    ('BMP图片', '*.bmp'),
    ('TIFF图片', '*.tiff;*.tif'),
    ('SVG矢量图', '*.svg'),
    ('PDF文档', '*.pdf')
]


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    支持开发环境和打包后的环境
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(CWD or os.getcwd(), relative_path)


def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)


# 初始化目录
def init_directories():
    """初始化必要的目录"""
    dirs = [DATA_DIR, FONT_DIR, STOPWORDS_DIR, CACHE_DIR]
    for d in dirs:
        ensure_dir(get_resource_path(d))
