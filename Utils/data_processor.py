# coding:utf-8
"""
数据处理模块
支持多数据源导入、文本清洗、分词功能
"""
import os
import re
import string
from typing import List, Dict, Tuple, Union, Optional

import pandas as pd
import jieba


class DataProcessor:
    """数据处理器类，负责数据导入、清洗和分词"""
    
    def __init__(self):
        self.stopwords = set()
        self.custom_dict_path = None
        self.default_stopwords_cn = os.path.join(os.path.dirname(__file__), '..', 'data', 'stopwords', 'cn_stopwords.txt')
        self.default_stopwords_en = os.path.join(os.path.dirname(__file__), '..', 'data', 'stopwords', 'en_stopwords.txt')
    
    def load_stopwords(self, filepath: Optional[str] = None, lang: str = 'cn') -> None:
        """加载停用词表"""
        if filepath is None:
            filepath = self.default_stopwords_cn if lang == 'cn' else self.default_stopwords_en
        
        if not os.path.exists(filepath):
            print(f"警告：停用词文件 {filepath} 不存在，使用空停用词表")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    self.stopwords.add(word)
    
    def add_stopwords(self, words: List[str]) -> None:
        """添加自定义停用词"""
        self.stopwords.update(words)
    
    def load_custom_dict(self, dict_path: str) -> None:
        """加载自定义词典"""
        if os.path.exists(dict_path):
            jieba.load_userdict(dict_path)
            self.custom_dict_path = dict_path
    
    def import_file(self, file_path: str) -> str:
        """导入单个文件（支持txt, csv, excel）"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return self._read_txt(file_path)
        elif ext == '.csv':
            return self._read_csv(file_path)
        elif ext in ['.xls', '.xlsx']:
            return self._read_excel(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def import_files(self, file_paths: List[str]) -> str:
        """批量导入多个文件"""
        all_text = []
        for path in file_paths:
            try:
                text = self.import_file(path)
                all_text.append(text)
            except Exception as e:
                print(f"导入文件 {path} 失败: {str(e)}")
        return '\n'.join(all_text)
    
    def _read_txt(self, file_path: str) -> str:
        """读取txt文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法识别文件编码: {file_path}")
    
    def _read_csv(self, file_path: str) -> str:
        """读取csv文件"""
        df = pd.read_csv(file_path)
        return self._df_to_text(df)
    
    def _read_excel(self, file_path: str) -> str:
        """读取excel文件"""
        df = pd.read_excel(file_path)
        return self._df_to_text(df)
    
    def _df_to_text(self, df: pd.DataFrame) -> str:
        """将DataFrame转换为文本字符串"""
        text_parts = []
        for col in df.columns:
            text_parts.extend(df[col].astype(str).tolist())
        return ' '.join(text_parts)
    
    def clean_text(self, text: str, remove_punct: bool = True, remove_numbers: bool = True, remove_special_chars: bool = True, remove_whitespace: bool = True, to_lower: bool = False) -> str:
        """文本清洗"""
        if to_lower:
            text = text.lower()
        
        if remove_punct:
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.translate(str.maketrans('', '', '。，、；：“”‘’（）【】《》！？·—…'))
        
        if remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        if remove_special_chars:
            text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text)
        
        if remove_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def segment(self, text: str, lang: str = 'cn', use_stopwords: bool = True) -> List[str]:
        """分词"""
        if lang == 'cn':
            words = list(jieba.cut(text))
        else:
            words = text.split()
        
        if use_stopwords:
            words = [w for w in words if w not in self.stopwords and w.strip()]
        
        return words
    
    def get_word_freq(self, words: List[str], top_n: Optional[int] = None) -> List[Tuple[str, int]]:
        """统计词频"""
        freq_dict = {}
        for word in words:
            if len(word) > 1:
                freq_dict[word] = freq_dict.get(word, 0) + 1
        
        sorted_freq = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
        
        if top_n:
            sorted_freq = sorted_freq[:top_n]
        
        return sorted_freq
    
    def process_file(self, file_path: str, lang: str = 'cn', stopwords_path: Optional[str] = None, custom_dict_path: Optional[str] = None, **clean_kwargs) -> Tuple[List[str], List[Tuple[str, int]]]:
        """处理单个文件：导入->清洗->分词->统计"""
        if stopwords_path:
            self.load_stopwords(stopwords_path)
        else:
            self.load_stopwords(lang=lang)
        
        if custom_dict_path:
            self.load_custom_dict(custom_dict_path)
        
        text = self.import_file(file_path)
        cleaned_text = self.clean_text(text, **clean_kwargs)
        words = self.segment(cleaned_text, lang=lang)
        word_freq = self.get_word_freq(words)
        
        return words, word_freq
