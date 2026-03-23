# coding:utf-8
"""
可视化模块
支持词云生成增强、词频统计可视化功能
"""
import os
from typing import List, Tuple, Dict, Optional, Union

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from matplotlib.font_manager import FontProperties

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """可视化类，负责词云生成和词频图表生成"""
    
    def __init__(self):
        self.wordcloud = None
        self.temp_dir = os.path.join(os.path.dirname(__file__), '..', 'data', '.catch')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_wordcloud(self, words: Union[List[str], Dict[str, int], str], font_path: str, width: int = 800, height: int = 600, background_color: str = 'white', mask: Optional[np.ndarray] = None, colormap: str = 'viridis', color_func=None, max_words: int = 200, min_font_size: int = 4, max_font_size: Optional[int] = None, prefer_horizontal: float = 0.9, scale: float = 1.0, margin: int = 2) -> WordCloud:
        """生成词云"""
        if isinstance(words, list):
            text = ' '.join(words)
            self.wordcloud = WordCloud(
                font_path=font_path,
                width=width,
                height=height,
                background_color=background_color,
                mask=mask,
                colormap=colormap,
                color_func=color_func,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                prefer_horizontal=prefer_horizontal,
                scale=scale,
                margin=margin
            ).generate(text)
        elif isinstance(words, dict):
            self.wordcloud = WordCloud(
                font_path=font_path,
                width=width,
                height=height,
                background_color=background_color,
                mask=mask,
                colormap=colormap,
                color_func=color_func,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                prefer_horizontal=prefer_horizontal,
                scale=scale,
                margin=margin
            ).generate_from_frequencies(words)
        else:
            self.wordcloud = WordCloud(
                font_path=font_path,
                width=width,
                height=height,
                background_color=background_color,
                mask=mask,
                colormap=colormap,
                color_func=color_func,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                prefer_horizontal=prefer_horizontal,
                scale=scale,
                margin=margin
            ).generate(words)
        
        return self.wordcloud
    
    def load_mask_image(self, mask_path: str) -> Optional[np.ndarray]:
        """加载蒙版图片"""
        if not os.path.exists(mask_path):
            return None
        
        mask = np.array(Image.open(mask_path))
        return mask
    
    def get_color_func_from_mask(self, mask: np.ndarray):
        """从蒙版图片获取颜色"""
        return ImageColorGenerator(mask)
    
    def save_wordcloud(self, save_path: str, dpi: int = 300) -> None:
        """保存词云图片"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        
        self.wordcloud.to_file(save_path)
    
    def get_wordcloud_image(self) -> Image.Image:
        """获取词云图片对象"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        
        return self.wordcloud.to_image()
    
    def plot_word_freq_chart(self, word_freq: List[Tuple[str, int]], top_n: int = 20, title: str = '词频统计TOP20', figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None, show_plot: bool = False) -> Optional[plt.Figure]:
        """生成词频柱状图"""
        if top_n > len(word_freq):
            top_n = len(word_freq)
        
        words = [item[0] for item in word_freq[:top_n]]
        freqs = [item[1] for item in word_freq[:top_n]]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        bars = ax.bar(words, freqs, color=plt.cm.viridis(np.linspace(0, 1, len(words))))
        
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel('词汇', fontsize=12)
        ax.set_ylabel('词频', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            return fig
    
    def plot_word_freq_pie(self, word_freq: List[Tuple[str, int]], top_n: int = 10, title: str = '词频分布饼图', figsize: Tuple[int, int] = (10, 10), save_path: Optional[str] = None, show_plot: bool = False) -> Optional[plt.Figure]:
        """生成词频饼图"""
        if top_n > len(word_freq):
            top_n = len(word_freq)
        
        words = [item[0] for item in word_freq[:top_n]]
        freqs = [item[1] for item in word_freq[:top_n]]
        
        total = sum(freq for _, freq in word_freq)
        other_freq = total - sum(freqs)
        
        if other_freq > 0:
            words.append('其他')
            freqs.append(other_freq)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        wedges, texts, autotexts = ax.pie(
            freqs,
            labels=words,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.viridis(np.linspace(0, 1, len(words)))
        )
        
        ax.set_title(title, fontsize=16, pad=20)
        plt.setp(texts, fontsize=10)
        plt.setp(autotexts, fontsize=8, weight='bold')
        
        ax.axis('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            return fig
    
    def plot_word_cloud_display(self, figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None, show_plot: bool = False) -> Optional[plt.Figure]:
        """显示词云"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(self.wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            return fig
    
    @staticmethod
    def get_available_colormaps() -> List[str]:
        """获取可用的颜色映射方案"""
        return ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic', 'twilight', 'twilight_shifted', 'hsv', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
