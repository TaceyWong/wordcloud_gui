# coding: utf-8
"""
可视化模块
支持词频统计柱状图、实时预览、颜色方案
"""

from __future__ import print_function, unicode_literals
import os
import sys
import io
import base64

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from PIL import Image

# 兼容Python 2/3
if sys.version_info[0] == 2:
    import cStringIO
    StringIO = cStringIO.StringIO
else:
    from io import BytesIO
    StringIO = BytesIO


class ColorScheme(object):
    """颜色方案类"""

    # 预定义颜色方案
    SCHEMES = {
        'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
        'warm': ['#ff6b6b', '#f9ca24', '#f0932b', '#eb4d4b', '#e55039',
                 '#fa8231', '#f7b731', '#d980fa', '#ff9ff3', '#feca57'],
        'cool': ['#4834d4', '#686de0', '#30336b', '#22a6b3', '#0984e3',
                 '#6c5ce7', '#00b894', '#00cec9', '#74b9ff', '#a29bfe'],
        'nature': ['#27ae60', '#2ecc71', '#16a085', '#1abc9c', '#2980b9',
                   '#3498db', '#8e44ad', '#9b59b6', '#2c3e50', '#34495e'],
        'sunset': ['#e74c3c', '#c0392b', '#e67e22', '#d35400', '#f39c12',
                   '#f1c40f', '#e84393', '#fd79a8', '#fdcb6e', '#e17055'],
        'ocean': ['#006266', '#009432', '#0652DD', '#9980FA', '#FDA7DF',
                  '#12CBC4', '#1289A7', '#D980FA', '#B53471', '#6F1E51'],
        'mono': ['#2d3436', '#636e72', '#b2bec3', '#dfe6e9', '#a4b0be',
                 '#747d8c', '#57606f', '#2f3542', '#ced6e0', '#f1f2f6'],
        'rainbow': ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#1abc9c',
                    '#3498db', '#9b59b6', '#34495e', '#16a085', '#27ae60']
    }

    @classmethod
    def get_scheme(cls, name='default'):
        """获取颜色方案"""
        return cls.SCHEMES.get(name, cls.SCHEMES['default'])

    @classmethod
    def get_all_schemes(cls):
        """获取所有颜色方案名称"""
        return list(cls.SCHEMES.keys())

    @classmethod
    def generate_custom_scheme(cls, base_color, count=10):
        """
        基于基础色生成自定义颜色方案
        :param base_color: 基础颜色（十六进制）
        :param count: 生成颜色数量
        :return: 颜色列表
        """
        from matplotlib.colors import to_rgb, to_hex
        import colorsys

        rgb = to_rgb(base_color)
        h, l, s = colorsys.rgb_to_hls(*rgb)

        colors = []
        for i in range(count):
            # 调整亮度和饱和度生成不同色调
            new_l = max(0.3, min(0.9, l + (i - count/2) * 0.1))
            new_s = max(0.3, min(1.0, s + (i - count/2) * 0.05))
            new_rgb = colorsys.hls_to_rgb(h, new_l, new_s)
            colors.append(to_hex(new_rgb))

        return colors


class WordFrequencyVisualizer(object):
    """词频可视化类"""

    def __init__(self, color_scheme='default'):
        self.color_scheme = ColorScheme.get_scheme(color_scheme)
        self.figsize = (12, 6)
        self.dpi = 100

    def set_color_scheme(self, scheme_name):
        """设置颜色方案"""
        self.color_scheme = ColorScheme.get_scheme(scheme_name)

    def plot_bar_chart(self, word_freq, top_n=20, title=u'词频统计TOP20',
                       horizontal=True, show_values=True):
        """
        绘制词频柱状图
        :param word_freq: 词频字典 {词: 频次}
        :param top_n: 显示前N个词
        :param title: 图表标题
        :param horizontal: 是否水平显示
        :param show_values: 是否显示数值
        :return: matplotlib图形对象
        """
        # 排序并取前N个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        words = [item[0] for item in sorted_words]
        freqs = [item[1] for item in sorted_words]

        # 创建图形
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # 选择颜色
        colors = self.color_scheme[:len(words)]

        if horizontal:
            # 水平柱状图
            bars = ax.barh(range(len(words)), freqs, color=colors)
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words)
            ax.invert_yaxis()  # 最高频在顶部
            ax.set_xlabel(u'频次', fontsize=12)
        else:
            # 垂直柱状图
            bars = ax.bar(range(len(words)), freqs, color=colors)
            ax.set_xticks(range(len(words)))
            ax.set_xticklabels(words, rotation=45, ha='right')
            ax.set_ylabel(u'频次', fontsize=12)

        # 设置标题
        ax.set_title(title, fontsize=14, fontweight='bold')

        # 显示数值
        if show_values:
            if horizontal:
                for i, (bar, freq) in enumerate(zip(bars, freqs)):
                    ax.text(bar.get_width() + max(freqs)*0.01, bar.get_y() + bar.get_height()/2,
                            str(freq), va='center', fontsize=9)
            else:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            '%d' % int(height), ha='center', va='bottom', fontsize=9)

        # 添加网格线
        ax.grid(axis='x' if horizontal else 'y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        return fig

    def save_bar_chart(self, word_freq, output_path, top_n=20, title=u'词频统计TOP20',
                       horizontal=True, format='png'):
        """
        保存词频柱状图
        :param word_freq: 词频字典
        :param output_path: 输出路径
        :param top_n: 显示前N个词
        :param title: 图表标题
        :param horizontal: 是否水平显示
        :param format: 输出格式
        """
        fig = self.plot_bar_chart(word_freq, top_n, title, horizontal)
        fig.savefig(output_path, format=format, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)

    def get_bar_chart_image(self, word_freq, top_n=20, title=u'词频统计TOP20',
                            horizontal=True):
        """
        获取词频柱状图图像数据（用于GUI显示）
        :param word_freq: 词频字典
        :param top_n: 显示前N个词
        :param title: 图表标题
        :param horizontal: 是否水平显示
        :return: PIL Image对象
        """
        fig = self.plot_bar_chart(word_freq, top_n, title, horizontal)

        # 保存到内存
        buf = StringIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)

        # 转换为PIL Image
        img = Image.open(buf)
        plt.close(fig)

        return img

    def get_bar_chart_bitmap(self, word_freq, top_n=20, title=u'词频统计TOP20',
                             horizontal=True):
        """
        获取词频柱状图wxBitmap（用于wxPython显示）
        :param word_freq: 词频字典
        :param top_n: 显示前N个词
        :param title: 图表标题
        :param horizontal: 是否水平显示
        :return: wx.Bitmap对象
        """
        import wx

        img = self.get_bar_chart_image(word_freq, top_n, title, horizontal)

        # 转换为wxBitmap
        if img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size
        data = img.tobytes()

        bitmap = wx.Bitmap.FromBuffer(width, height, data)
        return bitmap


class WordCloudPreview(object):
    """词云预览类"""

    def __init__(self):
        self.preview_size = (400, 300)

    def create_preview(self, wordcloud_obj, size=None):
        """
        创建词云预览
        :param wordcloud_obj: WordCloud对象
        :param size: 预览尺寸 (宽, 高)
        :return: PIL Image对象
        """
        if size is None:
            size = self.preview_size

        # 生成词云图像
        img = wordcloud_obj.to_image()

        # 调整尺寸
        img.thumbnail(size, Image.Resampling.LANCZOS)

        return img

    def get_preview_bitmap(self, wordcloud_obj, size=None):
        """
        获取词云预览wxBitmap
        :param wordcloud_obj: WordCloud对象
        :param size: 预览尺寸
        :return: wx.Bitmap对象
        """
        import wx

        img = self.create_preview(wordcloud_obj, size)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size
        data = img.tobytes()

        bitmap = wx.Bitmap.FromBuffer(width, height, data)
        return bitmap


class ThemeManager(object):
    """主题管理器 - 支持暗色/亮色主题"""

    THEMES = {
        'light': {
            'bg_color': '#ffffff',
            'fg_color': '#333333',
            'accent_color': '#0078d4',
            'panel_bg': '#f5f5f5',
            'border_color': '#dddddd',
            'chart_bg': '#ffffff',
            'chart_grid': '#eeeeee',
            'text_color': '#333333'
        },
        'dark': {
            'bg_color': '#2d2d30',
            'fg_color': '#cccccc',
            'accent_color': '#0078d4',
            'panel_bg': '#252526',
            'border_color': '#3e3e42',
            'chart_bg': '#2d2d30',
            'chart_grid': '#3e3e42',
            'text_color': '#cccccc'
        }
    }

    def __init__(self, theme='light'):
        self.current_theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES['light'])

    def set_theme(self, theme):
        """设置主题"""
        self.current_theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES['light'])

    def get_color(self, key):
        """获取颜色值"""
        return self.colors.get(key, self.colors['fg_color'])

    def apply_to_matplotlib(self):
        """应用主题到matplotlib"""
        theme = self.colors

        plt.rcParams['figure.facecolor'] = theme['bg_color']
        plt.rcParams['axes.facecolor'] = theme['chart_bg']
        plt.rcParams['axes.edgecolor'] = theme['border_color']
        plt.rcParams['axes.labelcolor'] = theme['text_color']
        plt.rcParams['text.color'] = theme['text_color']
        plt.rcParams['xtick.color'] = theme['text_color']
        plt.rcParams['ytick.color'] = theme['text_color']
        plt.rcParams['grid.color'] = theme['chart_grid']


if __name__ == "__main__":
    # 测试代码
    # 测试颜色方案
    print("可用颜色方案:", ColorScheme.get_all_schemes())
    print("默认方案:", ColorScheme.get_scheme('default'))

    # 测试词频可视化
    test_freq = {
        u'数据': 150,
        u'分析': 120,
        u'可视化': 100,
        u'Python': 90,
        u'词云': 85,
        u'统计': 80,
        u'图表': 75,
        u'机器学习': 70,
        u'人工智能': 65,
        u'大数据': 60,
        u'算法': 55,
        u'模型': 50,
        u'训练': 45,
        u'预测': 40,
        u'分类': 35
    }

    viz = WordFrequencyVisualizer('warm')
    viz.save_bar_chart(test_freq, 'test_chart.png', top_n=10)
    print("图表已保存到 test_chart.png")

    # 测试主题
    theme = ThemeManager('dark')
    print("暗色主题背景色:", theme.get_color('bg_color'))
