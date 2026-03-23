# coding:utf-8

import os
from typing import List, Tuple, Dict, Optional, Union
from collections import Counter

from PIL import Image
import numpy as np
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import jieba
import jieba.analyse


class MyWordCloud:
    
    def __init__(self):
        self.stopwords: set = set()
        self.seg_list: List[str] = []
        self.m_wordcloud: Optional[WordCloud] = None
        self.word_freq: List[Tuple[str, int]] = []
    
    def load_stopwords(self, filepath: str) -> set:
        self.stopwords = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.stopwords.add(word)
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.stopwords.add(word)
        return self.stopwords
    
    def add_stopwords(self, words: List[str]):
        for word in words:
            if word.strip():
                self.stopwords.add(word.strip())
    
    def load_custom_dict(self, filepath: str):
        jieba.load_userdict(filepath)
    
    def add_custom_word(self, word: str, freq: int = None, tag: str = None):
        if freq and tag:
            jieba.add_word(word, freq, tag)
        elif freq:
            jieba.add_word(word, freq)
        else:
            jieba.add_word(word)
    
    def cut_text(self, text: str, 
                 remove_stopwords: bool = True,
                 cut_all: bool = False,
                 HMM: bool = True) -> List[str]:
        words = list(jieba.cut(text, cut_all=cut_all, HMM=HMM))
        words = [w.strip() for w in words if w.strip()]
        
        if remove_stopwords:
            words = [w for w in words if w not in self.stopwords]
        
        self.seg_list = words
        return self.seg_list
    
    def cut_file(self, filepath: str, 
                 remove_stopwords: bool = True,
                 encoding: str = 'utf-8') -> List[str]:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                text = f.read()
        
        return self.cut_text(text, remove_stopwords)
    
    def get_word_frequency(self, words: List[str] = None, 
                           top_n: int = None) -> List[Tuple[str, int]]:
        if words is None:
            words = self.seg_list
        
        counter = Counter(words)
        self.word_freq = counter.most_common(top_n) if top_n else counter.most_common()
        return self.word_freq
    
    def extract_keywords(self, text: str, 
                         top_k: int = 20,
                         with_weight: bool = False) -> List[Union[str, Tuple[str, float]]]:
        if with_weight:
            return jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        else:
            return jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
    
    def extract_keywords_textrank(self, text: str,
                                   top_k: int = 20,
                                   with_weight: bool = False) -> List[Union[str, Tuple[str, float]]]:
        if with_weight:
            return jieba.analyse.textrank(text, topK=top_k, withWeight=True)
        else:
            return jieba.analyse.textrank(text, topK=top_k, withWeight=False)
    
    def words_to_text(self, words: List[str] = None) -> str:
        if words is None:
            words = self.seg_list
        return ' '.join(words)
    
    def load_mask(self, mask_path: str, 
                  threshold: int = 128) -> np.ndarray:
        mask_img = Image.open(mask_path)
        if mask_img.mode != 'L':
            mask_img = mask_img.convert('L')
        mask_array = np.array(mask_img)
        mask_array = mask_array > threshold
        return mask_array
    
    def load_mask_with_colors(self, mask_path: str) -> Tuple[np.ndarray, np.ndarray]:
        mask_img = Image.open(mask_path)
        if mask_img.mode == 'RGBA':
            mask_img = mask_img.convert('RGB')
        elif mask_img.mode != 'RGB':
            mask_img = mask_img.convert('RGB')
        
        mask_array = np.array(mask_img)
        gray = mask_img.convert('L')
        mask = np.array(gray) < 128
        
        return mask, mask_array
    
    def generate_wordcloud(self,
                           text: str = None,
                           word_freq: List[Tuple[str, int]] = None,
                           font_path: str = None,
                           width: int = 800,
                           height: int = 600,
                           margin: int = 5,
                           background_color: str = 'white',
                           max_font_size: int = None,
                           min_font_size: int = 10,
                           max_words: int = 200,
                           mask: np.ndarray = None,
                           colormap: str = 'viridis',
                           color_func = None,
                           prefer_horizontal: float = 0.9,
                           scale: int = 1,
                           relative_scaling: float = 0.5,
                           min_word_length: int = 0,
                           repeat: bool = False,
                           include_numbers: bool = False,
                           mode: str = 'RGB') -> WordCloud:
        
        wc_params = {
            'width': width,
            'height': height,
            'margin': margin,
            'background_color': background_color,
            'max_words': max_words,
            'prefer_horizontal': prefer_horizontal,
            'scale': scale,
            'relative_scaling': relative_scaling,
            'min_word_length': min_word_length,
            'repeat': repeat,
            'include_numbers': include_numbers,
            'mode': mode,
        }
        
        if font_path:
            wc_params['font_path'] = font_path
        
        if max_font_size:
            wc_params['max_font_size'] = max_font_size
        
        if min_font_size:
            wc_params['min_font_size'] = min_font_size
        
        if mask is not None:
            wc_params['mask'] = mask
        
        if colormap:
            wc_params['colormap'] = colormap
        
        if color_func:
            wc_params['color_func'] = color_func
        
        self.m_wordcloud = WordCloud(**wc_params)
        
        if word_freq:
            self.m_wordcloud = self.m_wordcloud.generate_from_frequencies(dict(word_freq))
        elif text:
            self.m_wordcloud = self.m_wordcloud.generate(text)
        else:
            text = self.words_to_text()
            self.m_wordcloud = self.m_wordcloud.generate(text)
        
        return self.m_wordcloud
    
    def recolor(self, colormap: str = None, color_func = None, random_state: int = None):
        if self.m_wordcloud:
            if colormap:
                self.m_wordcloud.recolor(colormap=colormap, random_state=random_state)
            elif color_func:
                self.m_wordcloud.recolor(color_func=color_func, random_state=random_state)
        return self.m_wordcloud
    
    def to_array(self) -> np.ndarray:
        if self.m_wordcloud:
            return self.m_wordcloud.to_array()
        return None
    
    def to_file(self, filepath: str):
        if self.m_wordcloud:
            self.m_wordcloud.to_file(filepath)
    
    def to_image(self) -> Image.Image:
        if self.m_wordcloud:
            return self.m_wordcloud.to_image()
        return None
    
    def get_words(self) -> List[str]:
        if self.m_wordcloud:
            return list(self.m_wordcloud.words_.keys())
        return []


class WordCloudBuilder:
    
    PRESET_COLORMAPS = [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis',
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
        'twilight', 'twilight_shifted', 'hsv',
        'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
        'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c'
    ]
    
    PRESET_SHAPES = {
        'rectangle': None,
        'circle': 'circle',
        'heart': 'heart',
        'star': 'star',
    }
    
    def __init__(self):
        self.wc = MyWordCloud()
        self.config: Dict = {}
    
    def set_text(self, text: str):
        self.config['text'] = text
        return self
    
    def set_words(self, words: List[str]):
        self.config['words'] = words
        return self
    
    def set_word_freq(self, word_freq: List[Tuple[str, int]]):
        self.config['word_freq'] = word_freq
        return self
    
    def set_font(self, font_path: str):
        self.config['font_path'] = font_path
        return self
    
    def set_size(self, width: int, height: int):
        self.config['width'] = width
        self.config['height'] = height
        return self
    
    def set_background(self, color: str):
        self.config['background_color'] = color
        return self
    
    def set_mask(self, mask_path: str):
        self.config['mask_path'] = mask_path
        return self
    
    def set_colormap(self, colormap: str):
        self.config['colormap'] = colormap
        return self
    
    def set_max_words(self, max_words: int):
        self.config['max_words'] = max_words
        return self
    
    def set_font_size(self, max_size: int = None, min_size: int = None):
        if max_size:
            self.config['max_font_size'] = max_size
        if min_size:
            self.config['min_font_size'] = min_size
        return self
    
    def set_stopwords(self, stopwords_path: str):
        self.wc.load_stopwords(stopwords_path)
        return self
    
    def build(self) -> WordCloud:
        text = self.config.get('text')
        words = self.config.get('words')
        word_freq = self.config.get('word_freq')
        
        if words and not text and not word_freq:
            text = self.wc.words_to_text(words)
        
        mask = None
        if self.config.get('mask_path'):
            mask = self.wc.load_mask(self.config['mask_path'])
        
        return self.wc.generate_wordcloud(
            text=text,
            word_freq=word_freq,
            font_path=self.config.get('font_path'),
            width=self.config.get('width', 800),
            height=self.config.get('height', 600),
            margin=self.config.get('margin', 5),
            background_color=self.config.get('background_color', 'white'),
            max_font_size=self.config.get('max_font_size'),
            min_font_size=self.config.get('min_font_size', 10),
            max_words=self.config.get('max_words', 200),
            mask=mask,
            colormap=self.config.get('colormap', 'viridis'),
            prefer_horizontal=self.config.get('prefer_horizontal', 0.9),
            scale=self.config.get('scale', 1),
        )


def create_wordcloud_simple(text: str,
                            font_path: str = None,
                            width: int = 800,
                            height: int = 600,
                            background_color: str = 'white',
                            colormap: str = 'viridis',
                            stopwords_path: str = None) -> WordCloud:
    wc = MyWordCloud()
    
    if stopwords_path:
        wc.load_stopwords(stopwords_path)
    
    words = wc.cut_text(text, remove_stopwords=True)
    word_text = wc.words_to_text(words)
    
    return wc.generate_wordcloud(
        text=word_text,
        font_path=font_path,
        width=width,
        height=height,
        background_color=background_color,
        colormap=colormap
    )


if __name__ == "__main__":
    test_text = """
    Python是一种广泛使用的高级编程语言，由Guido van Rossum于1991年首次发布。
    Python的设计哲学强调代码的可读性和简洁性，它的语法允许程序员用更少的代码行表达概念。
    Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
    Python拥有一个庞大而活跃的社区，提供了大量的第三方库和框架。
    """
    
    wc = MyWordCloud()
    words = wc.cut_text(test_text)
    print("分词结果:", words[:10])
    
    freq = wc.get_word_frequency(top_n=10)
    print("词频统计:", freq)
    
    wordcloud = wc.generate_wordcloud(
        text=wc.words_to_text(),
        width=800,
        height=400,
        background_color='white'
    )
    
    if wordcloud:
        wordcloud.to_file("test_wordcloud.png")
        print("词云已保存到 test_wordcloud.png")
