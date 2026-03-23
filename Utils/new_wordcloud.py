# coding:utf-8
"""
增强版词云生成模块
支持蒙版、颜色方案、实时预览等功能
"""
import os
from typing import List, Tuple, Dict, Optional, Union

import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import jieba

from Utils.data_processor import DataProcessor
from Utils.visualizer import Visualizer


class MyWordCloud:
    """增强版词云生成类"""
    
    def __init__(self):
        self.stopwords = set()
        self.seg_list = []
        self.wordcloud = None
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        self.current_params = {}
    
    def load_stopwords(self, filename: str) -> set:
        """加载停用词表"""
        self.stopwords = set()
        if not os.path.exists(filename):
            print(f"警告：停用词文件 {filename} 不存在")
            return self.stopwords
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    self.stopwords.add(word)
        return self.stopwords
    
    def word_cut(self, stopwords: set, input_text: Union[str, List[str]]) -> str:
        """分词处理"""
        if isinstance(input_text, list):
            text = ' '.join(input_text)
        else:
            text = input_text
        
        seg_generator = jieba.cut(text)
        seg_list = [i for i in seg_generator if i not in stopwords and i.strip()]
        seg_list = [i for i in seg_list if i != u' ']
        self.seg_list = ' '.join(seg_list)
        return self.seg_list
    
    def process_text_file(self, file_path: str, stopwords_path: Optional[str] = None) -> Tuple[str, List[Tuple[str, int]]]:
        """处理文本文件，返回分词结果和词频统计"""
        if stopwords_path:
            stopwords = self.load_stopwords(stopwords_path)
        else:
            stopwords = self.stopwords
        
        text = self.data_processor.import_file(file_path)
        cleaned_text = self.data_processor.clean_text(text)
        words = self.data_processor.segment(cleaned_text, use_stopwords=True)
        word_freq = self.data_processor.get_word_freq(words)
        
        return ' '.join(words), word_freq
    
    def gen_wordcloud(self, seg_list: Union[str, List[str], Dict[str, int]], font_path: str, background_color: str = "white", margin: int = 2, width: int = 800, height: int = 600, flag: int = 1, mask: Optional[np.ndarray] = None, colormap: str = 'viridis', color_func=None, max_words: int = 200, min_font_size: int = 4, max_font_size: Optional[int] = None, prefer_horizontal: float = 0.9, scale: float = 1.0) -> WordCloud:
        """生成词云（增强版）"""
        self.current_params = {
            'seg_list': seg_list,
            'font_path': font_path,
            'background_color': background_color,
            'margin': margin,
            'width': width,
            'height': height,
            'flag': flag,
            'mask': mask,
            'colormap': colormap,
            'color_func': color_func,
            'max_words': max_words,
            'min_font_size': min_font_size,
            'max_font_size': max_font_size,
            'prefer_horizontal': prefer_horizontal,
            'scale': scale
        }
        
        if flag == 0:
            freq_dict = seg_list if isinstance(seg_list, dict) else dict(seg_list)
            self.wordcloud = WordCloud(
                font_path=font_path,
                background_color=background_color,
                margin=margin,
                width=width,
                height=height,
                mask=mask,
                colormap=colormap,
                color_func=color_func,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                prefer_horizontal=prefer_horizontal,
                scale=scale
            ).generate_from_frequencies(freq_dict)
        else:
            if isinstance(seg_list, list):
                text = ' '.join(seg_list)
            else:
                text = seg_list
            
            self.wordcloud = WordCloud(
                font_path=font_path,
                background_color=background_color,
                margin=margin,
                width=width,
                height=height,
                mask=mask,
                colormap=colormap,
                color_func=color_func,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                prefer_horizontal=prefer_horizontal,
                scale=scale
            ).generate(text)
        
        return self.wordcloud
    
    def regenerate_with_params(self, **kwargs) -> WordCloud:
        """使用新参数重新生成词云（用于实时预览）"""
        if not self.current_params:
            raise ValueError("请先生成词云")
        
        params = self.current_params.copy()
        params.update(kwargs)
        
        return self.gen_wordcloud(**params)
    
    def load_mask(self, mask_path: str) -> Optional[np.ndarray]:
        """加载蒙版图片"""
        return self.visualizer.load_mask_image(mask_path)
    
    def get_image_color_func(self, mask: np.ndarray):
        """获取基于蒙版图片的颜色方案"""
        return ImageColorGenerator(mask)
    
    def get_word_freq_chart(self, word_freq: List[Tuple[str, int]], top_n: int = 20, save_path: Optional[str] = None):
        """生成词频统计图表"""
        return self.visualizer.plot_word_freq_chart(word_freq, top_n, save_path=save_path)
    
    def to_image(self):
        """获取词云图片对象"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        return self.wordcloud.to_image()
    
    def to_file(self, filename: str):
        """保存词云到文件"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        self.wordcloud.to_file(filename)
    
    def get_array(self):
        """获取词云numpy数组"""
        if self.wordcloud is None:
            raise ValueError("请先生成词云")
        return self.wordcloud.to_array()
    
    @staticmethod
    def get_available_colormaps() -> List[str]:
        """获取可用的颜色映射方案"""
        return Visualizer.get_available_colormaps()
