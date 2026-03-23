# coding:utf-8

import os
import re
import string
from collections import Counter
from typing import List, Dict, Tuple, Optional, Union

import pandas as pd
import jieba
import jieba.analyse


class DataProcessor:
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self.stopwords: set = set()
        self.custom_words: set = set()
        self._init_default_settings()
    
    def _init_default_settings(self):
        cn_stopwords_path = os.path.join(self.base_dir, "data", "stopwords", "cn_stopwords.txt")
        en_stopwords_path = os.path.join(self.base_dir, "data", "stopwords", "en_stopwords.txt")
        
        if os.path.exists(cn_stopwords_path):
            self.load_stopwords(cn_stopwords_path)
        if os.path.exists(en_stopwords_path):
            self.load_stopwords(en_stopwords_path)
    
    def load_stopwords(self, filepath: str) -> int:
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.stopwords.add(word)
                        count += 1
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.stopwords.add(word)
                        count += 1
        return count
    
    def add_stopwords(self, words: List[str]):
        for word in words:
            if word.strip():
                self.stopwords.add(word.strip())
    
    def load_custom_dict(self, filepath: str):
        jieba.load_userdict(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    self.custom_words.add(parts[0])
    
    def add_custom_words(self, words: List[str]):
        for word in words:
            if word.strip():
                jieba.add_word(word.strip())
                self.custom_words.add(word.strip())
    
    def load_excel(self, filepath: str, sheet_name: Union[str, int, None] = 0, 
                   column: Optional[str] = None) -> str:
        try:
            if sheet_name is None:
                df = pd.read_excel(filepath)
            else:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            if column and column in df.columns:
                text = df[column].astype(str).str.cat(sep=' ')
            else:
                text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
            
            return text
        except Exception as e:
            raise ValueError(f"Excel文件读取失败: {str(e)}")
    
    def load_csv(self, filepath: str, column: Optional[str] = None, 
                 encoding: str = 'utf-8') -> str:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            
            if column and column in df.columns:
                text = df[column].astype(str).str.cat(sep=' ')
            else:
                text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
            
            return text
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='gbk')
            if column and column in df.columns:
                text = df[column].astype(str).str.cat(sep=' ')
            else:
                text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
            return text
        except Exception as e:
            raise ValueError(f"CSV文件读取失败: {str(e)}")
    
    def load_txt(self, filepath: str, encoding: str = 'utf-8') -> str:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"TXT文件读取失败: {str(e)}")
    
    def load_file(self, filepath: str, **kwargs) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            return self.load_excel(filepath, **kwargs)
        elif ext == '.csv':
            return self.load_csv(filepath, **kwargs)
        elif ext == '.txt':
            return self.load_txt(filepath, **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def load_multiple_files(self, filepaths: List[str], **kwargs) -> str:
        texts = []
        for filepath in filepaths:
            text = self.load_file(filepath, **kwargs)
            texts.append(text)
        return ' '.join(texts)
    
    def clean_text(self, text: str, 
                   remove_punctuation: bool = True,
                   remove_digits: bool = True,
                   remove_special_chars: bool = True,
                   remove_whitespace: bool = True,
                   min_word_length: int = 1) -> str:
        if not text:
            return ""
        
        if remove_special_chars:
            text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        if remove_punctuation:
            punctuation = string.punctuation + '，。！？；：""''（）【】《》、·…—～'
            text = text.translate(str.maketrans(punctuation, ' ' * len(punctuation)))
        
        if remove_digits:
            text = re.sub(r'\d+', ' ', text)
        
        if remove_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def segment_text(self, text: str, 
                      remove_stopwords: bool = True,
                      lang: str = 'auto') -> List[str]:
        if not text:
            return []
        
        if lang == 'auto':
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            total_chars = len(re.findall(r'\w', text))
            lang = 'zh' if chinese_chars > total_chars * 0.3 else 'en'
        
        if lang == 'zh':
            words = list(jieba.cut(text))
        else:
            words = text.split()
        
        words = [w.strip() for w in words if w.strip()]
        
        if remove_stopwords:
            words = [w for w in words if w not in self.stopwords]
        
        return words
    
    def process_text(self, text: str,
                     clean_options: Optional[Dict] = None,
                     segment_options: Optional[Dict] = None) -> List[str]:
        if clean_options is None:
            clean_options = {
                'remove_punctuation': True,
                'remove_digits': True,
                'remove_special_chars': True,
                'remove_whitespace': True
            }
        
        if segment_options is None:
            segment_options = {
                'remove_stopwords': True,
                'lang': 'auto'
            }
        
        cleaned_text = self.clean_text(text, **clean_options)
        words = self.segment_text(cleaned_text, **segment_options)
        
        return words
    
    def process_file(self, filepath: str,
                     clean_options: Optional[Dict] = None,
                     segment_options: Optional[Dict] = None,
                     **load_kwargs) -> List[str]:
        text = self.load_file(filepath, **load_kwargs)
        return self.process_text(text, clean_options, segment_options)
    
    def get_word_frequency(self, words: List[str], top_n: int = None) -> List[Tuple[str, int]]:
        counter = Counter(words)
        if top_n:
            return counter.most_common(top_n)
        return counter.most_common()
    
    def words_to_text(self, words: List[str]) -> str:
        return ' '.join(words)
    
    def frequency_to_dict(self, freq_list: List[Tuple[str, int]]) -> Dict[str, int]:
        return dict(freq_list)
    
    def get_file_columns(self, filepath: str) -> List[str]:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath, nrows=0)
            return list(df.columns)
        elif ext == '.csv':
            try:
                df = pd.read_csv(filepath, encoding='utf-8', nrows=0)
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding='gbk', nrows=0)
            return list(df.columns)
        else:
            return []
    
    def get_excel_sheets(self, filepath: str) -> List[str]:
        try:
            xl = pd.ExcelFile(filepath)
            return xl.sheet_names
        except Exception:
            return []


class TextCleaner:
    
    def __init__(self):
        self.patterns = {
            'html': re.compile(r'<[^>]+>'),
            'url': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'1[3-9]\d{9}'),
            'whitespace': re.compile(r'\s+'),
            'chinese_punctuation': re.compile(r'[，。！？；：""''（）【】《》、·…—～]'),
            'english_punctuation': re.compile(r'[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]'),
            'digits': re.compile(r'\d+'),
        }
    
    def remove_html(self, text: str) -> str:
        return self.patterns['html'].sub(' ', text)
    
    def remove_urls(self, text: str) -> str:
        return self.patterns['url'].sub(' ', text)
    
    def remove_emails(self, text: str) -> str:
        return self.patterns['email'].sub(' ', text)
    
    def remove_phones(self, text: str) -> str:
        return self.patterns['phone'].sub(' ', text)
    
    def normalize_whitespace(self, text: str) -> str:
        return self.patterns['whitespace'].sub(' ', text).strip()
    
    def clean_all(self, text: str, 
                  remove_html: bool = True,
                  remove_urls: bool = True,
                  remove_emails: bool = True,
                  remove_phones: bool = True) -> str:
        if remove_html:
            text = self.remove_html(text)
        if remove_urls:
            text = self.remove_urls(text)
        if remove_emails:
            text = self.remove_emails(text)
        if remove_phones:
            text = self.remove_phones(text)
        return self.normalize_whitespace(text)


if __name__ == "__main__":
    processor = DataProcessor()
    test_text = "这是一个测试文本，包含一些标点符号！还有数字123。"
    words = processor.process_text(test_text)
    print(words)
    freq = processor.get_word_frequency(words, top_n=10)
    print(freq)
