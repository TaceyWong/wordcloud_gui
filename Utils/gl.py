# coding:utf-8

import os
import sys
import platform
from typing import Dict, Any


def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CWD = get_base_dir()


def get_path(*paths) -> str:
    return os.path.join(CWD, *paths)


def get_data_path(*paths) -> str:
    return get_path('data', *paths)


def get_font_path(font_name: str) -> str:
    return get_data_path('font', f'{font_name}.ttf')


def get_stopwords_path(lang: str = 'cn') -> str:
    return get_data_path('stopwords', f'{lang}_stopwords.txt')


def get_bitmap_path(filename: str) -> str:
    return get_path('bitmaps', filename)


def get_catch_dir() -> str:
    catch_dir = get_data_path('.catch')
    if not os.path.exists(catch_dir):
        os.makedirs(catch_dir)
    return catch_dir


BITMAP_DIR = 'bitmaps/'


TIME_NOW = None


IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'


PATH_SEP = os.sep


THEMES: Dict[str, Dict[str, Any]] = {
    'light': {
        'name': '亮色主题',
        'bg_color': '#F5F5F5',
        'panel_bg': '#FFFFFF',
        'text_color': '#333333',
        'accent_color': '#3498DB',
        'button_bg': '#3498DB',
        'button_text': '#FFFFFF',
        'input_bg': '#FFFFFF',
        'border_color': '#DDDDDD',
        'highlight_color': '#E8F4FD',
        'statusbar_bg': '#E0E0E0',
    },
    'dark': {
        'name': '暗色主题',
        'bg_color': '#2C3E50',
        'panel_bg': '#34495E',
        'text_color': '#ECF0F1',
        'accent_color': '#3498DB',
        'button_bg': '#3498DB',
        'button_text': '#FFFFFF',
        'input_bg': '#2C3E50',
        'border_color': '#4A6785',
        'highlight_color': '#3D5A73',
        'statusbar_bg': '#233140',
    }
}


CURRENT_THEME = 'light'


def get_current_theme() -> Dict[str, Any]:
    return THEMES.get(CURRENT_THEME, THEMES['light'])


def set_theme(theme_name: str):
    global CURRENT_THEME
    if theme_name in THEMES:
        CURRENT_THEME = theme_name
        return True
    return False


def get_theme_color(color_key: str) -> str:
    theme = get_current_theme()
    return theme.get(color_key, '#000000')


APP_NAME = 'WordCloud-GUI'
APP_VERSION = '2.0.0'
APP_AUTHOR = 'Tacey Wong'


DEFAULT_WORDCLOUD_CONFIG = {
    'width': 800,
    'height': 600,
    'margin': 5,
    'background_color': 'white',
    'max_font_size': 40,
    'min_font_size': 10,
    'max_words': 200,
    'prefer_horizontal': 0.9,
    'scale': 1,
    'colormap': 'viridis',
}


DEFAULT_CLEAN_CONFIG = {
    'remove_punctuation': True,
    'remove_digits': True,
    'remove_special_chars': True,
    'remove_whitespace': True,
    'min_word_length': 1,
}


DEFAULT_EXPORT_CONFIG = {
    'format': 'png',
    'dpi': 300,
    'quality': 95,
}


def ensure_catch_dir():
    catch_dir = get_catch_dir()
    if not os.path.exists(catch_dir):
        os.makedirs(catch_dir)
    return catch_dir


def cleanup_catch_dir():
    catch_dir = get_catch_dir()
    if os.path.exists(catch_dir):
        import shutil
        try:
            shutil.rmtree(catch_dir)
            os.makedirs(catch_dir)
        except Exception as e:
            print(f"清理缓存目录失败: {e}")


def get_available_fonts() -> list:
    font_dir = get_data_path('font')
    fonts = []
    if os.path.exists(font_dir):
        for filename in os.listdir(font_dir):
            if filename.endswith('.ttf') or filename.endswith('.otf'):
                fonts.append(os.path.splitext(filename)[0])
    return fonts


def get_available_stopwords() -> list:
    stopwords_dir = get_data_path('stopwords')
    stopwords = []
    if os.path.exists(stopwords_dir):
        for filename in os.listdir(stopwords_dir):
            if filename.endswith('.txt'):
                lang = filename.replace('_stopwords.txt', '')
                stopwords.append(lang)
    return stopwords


def get_system_info() -> Dict[str, str]:
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
    }
