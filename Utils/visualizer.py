# coding:utf-8

import os
import io
from typing import List, Tuple, Dict, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np


plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class FrequencyVisualizer:
    
    def __init__(self, style: str = 'seaborn-v0_8-whitegrid'):
        self.style = style
        self.available_styles = plt.style.available
        if style not in self.available_styles:
            self.style = 'seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in self.available_styles else 'ggplot'
    
    def create_bar_chart(self, 
                         word_freq: List[Tuple[str, int]], 
                         title: str = '词频统计 TOP20',
                         xlabel: str = '词语',
                         ylabel: str = '频次',
                         top_n: int = 20,
                         figsize: Tuple[int, int] = (12, 6),
                         color: str = '#3498db',
                         rotation: int = 45,
                         show_values: bool = True) -> Figure:
        if not word_freq:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=16)
            return fig
        
        data = word_freq[:top_n]
        words = [item[0] for item in data]
        freqs = [item[1] for item in data]
        
        with plt.style.context(self.style):
            fig, ax = plt.subplots(figsize=figsize)
            
            x_pos = np.arange(len(words))
            bars = ax.bar(x_pos, freqs, color=color, edgecolor='white', linewidth=0.7)
            
            if show_values:
                for bar, freq in zip(bars, freqs):
                    height = bar.get_height()
                    ax.annotate(f'{freq}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=9)
            
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(words, rotation=rotation, ha='right')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
        
        return fig
    
    def create_horizontal_bar_chart(self,
                                    word_freq: List[Tuple[str, int]],
                                    title: str = '词频统计 TOP20',
                                    xlabel: str = '频次',
                                    ylabel: str = '词语',
                                    top_n: int = 20,
                                    figsize: Tuple[int, int] = (10, 8),
                                    color: str = '#e74c3c',
                                    show_values: bool = True) -> Figure:
        if not word_freq:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=16)
            return fig
        
        data = word_freq[:top_n]
        data = data[::-1]
        words = [item[0] for item in data]
        freqs = [item[1] for item in data]
        
        with plt.style.context(self.style):
            fig, ax = plt.subplots(figsize=figsize)
            
            y_pos = np.arange(len(words))
            bars = ax.barh(y_pos, freqs, color=color, edgecolor='white', linewidth=0.7)
            
            if show_values:
                for bar, freq in zip(bars, freqs):
                    width = bar.get_width()
                    ax.annotate(f'{freq}',
                               xy=(width, bar.get_y() + bar.get_height() / 2),
                               xytext=(3, 0),
                               textcoords="offset points",
                               ha='left', va='center', fontsize=9)
            
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(words)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
        
        return fig
    
    def create_pie_chart(self,
                         word_freq: List[Tuple[str, int]],
                         title: str = '词频分布',
                         top_n: int = 10,
                         figsize: Tuple[int, int] = (10, 8),
                         show_percentage: bool = True) -> Figure:
        if not word_freq:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=16)
            return fig
        
        data = word_freq[:top_n]
        words = [item[0] for item in data]
        freqs = [item[1] for item in data]
        
        if len(word_freq) > top_n:
            other_freq = sum(item[1] for item in word_freq[top_n:])
            words.append('其他')
            freqs.append(other_freq)
        
        with plt.style.context(self.style):
            fig, ax = plt.subplots(figsize=figsize)
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(words)))
            
            wedges, texts, autotexts = ax.pie(freqs, labels=words, autopct='%1.1f%%',
                                              colors=colors, startangle=90,
                                              wedgeprops=dict(edgecolor='white'))
            
            if show_percentage:
                for autotext in autotexts:
                    autotext.set_fontsize(9)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            
            plt.tight_layout()
        
        return fig
    
    def create_wordcloud_comparison(self,
                                    wordcloud1,
                                    wordcloud2,
                                    title1: str = '词云1',
                                    title2: str = '词云2',
                                    figsize: Tuple[int, int] = (16, 6)) -> Figure:
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        axes[0].imshow(wordcloud1, interpolation='bilinear')
        axes[0].axis('off')
        axes[0].set_title(title1, fontsize=14, fontweight='bold')
        
        axes[1].imshow(wordcloud2, interpolation='bilinear')
        axes[1].axis('off')
        axes[1].set_title(title2, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def figure_to_image(self, fig: Figure) -> bytes:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()
    
    def figure_to_file(self, fig: Figure, filepath: str, dpi: int = 150):
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    
    def close_figure(self, fig: Figure):
        plt.close(fig)


class ThemeManager:
    
    THEMES = {
        'light': {
            'bg_color': '#FFFFFF',
            'text_color': '#000000',
            'grid_color': '#E0E0E0',
            'bar_color': '#3498db',
            'accent_color': '#e74c3c'
        },
        'dark': {
            'bg_color': '#2C3E50',
            'text_color': '#ECF0F1',
            'grid_color': '#34495E',
            'bar_color': '#3498db',
            'accent_color': '#e74c3c'
        }
    }
    
    @classmethod
    def get_theme(cls, theme_name: str) -> Dict:
        return cls.THEMES.get(theme_name, cls.THEMES['light'])
    
    @classmethod
    def apply_theme_to_figure(cls, fig, ax, theme_name: str = 'light'):
        theme = cls.get_theme(theme_name)
        
        fig.patch.set_facecolor(theme['bg_color'])
        ax.set_facecolor(theme['bg_color'])
        
        ax.tick_params(colors=theme['text_color'])
        ax.xaxis.label.set_color(theme['text_color'])
        ax.yaxis.label.set_color(theme['text_color'])
        ax.title.set_color(theme['text_color'])
        
        for spine in ax.spines.values():
            spine.set_color(theme['grid_color'])


if __name__ == "__main__":
    test_data = [('Python', 100), ('Java', 80), ('JavaScript', 70), 
                 ('C++', 60), ('Go', 50), ('Rust', 40)]
    
    viz = FrequencyVisualizer()
    fig = viz.create_bar_chart(test_data, title='编程语言热度 TOP10')
    viz.figure_to_file(fig, 'test_bar_chart.png')
    print("图表已保存")
