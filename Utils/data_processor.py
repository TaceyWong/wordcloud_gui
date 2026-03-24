# coding: utf-8
"""
数据处理模块
支持Excel/CSV/TXT文件导入、文本清洗、分词处理
"""

from __future__ import print_function, unicode_literals
import os
import re
import sys
import jieba
import pandas as pd
import numpy as np
from collections import Counter

# 兼容Python 2/3
if sys.version_info[0] == 2:
    import codecs
    open = codecs.open


class DataProcessor(object):
    """数据处理类：负责文件导入、文本清洗、分词"""

    def __init__(self):
        self.stopwords = set()
        self.custom_dict = None
        self.text_content = ""
        self.word_freq = {}

    def load_stopwords(self, filepath=None):
        """
        加载停用词表
        :param filepath: 停用词文件路径，如果为None则使用默认停用词
        :return: 停用词集合
        """
        self.stopwords = set()

        # 加载默认中文停用词
        default_cn_stopwords = [
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这些', '那些', '这个', '那个', '之', '与', '及', '等',
            '可以', '为', '或', '但', '而', '因为', '所以', '如果', '就', '让', '向', '到', '把', '被', '将', '从', '对',
            '我们', '你们', '他们', '她们', '它们', '咱们', '大家', '大伙儿', '人家', '别人', '本人', '本身', '本', '此',
            '它', '他', '她', '我', '你', '哪', '什么', '谁', '怎么', '怎样', '为什么', '如何', '多少', '几',
            '和', '跟', '同', '与', '而', '或', '但', '却', '因为', '所以', '虽然', '尽管', '即使', '哪怕', '不管', '无论',
            '的', '地', '得', '着', '了', '过', '把', '被', '让', '给', '向', '往', '在', '从', '到', '于', '关于', '对于',
            '啊', '呢', '吧', '吗', '嘛', '呗', '哇', '呀', '哪', '哦', '哈', '哟', '唉', '哎', '嘿', '嗨', '哼', '哼',
            '零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]
        self.stopwords.update(default_cn_stopwords)

        # 加载默认英文停用词
        default_en_stopwords = [
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'now', 'then', 'here', 'there'
        ]
        self.stopwords.update(default_en_stopwords)

        # 加载自定义停用词文件
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            self.stopwords.add(word)
            except Exception as e:
                print("加载停用词文件失败: {}".format(e))

        return self.stopwords

    def add_custom_stopwords(self, words):
        """
        添加自定义停用词
        :param words: 停用词列表或字符串（逗号/空格分隔）
        """
        if isinstance(words, str):
            words = re.split(r'[,，\s]+', words)
        self.stopwords.update([w.strip() for w in words if w.strip()])

    def load_custom_dict(self, filepath):
        """
        加载自定义词典（jieba格式）
        :param filepath: 词典文件路径
        """
        if os.path.exists(filepath):
            jieba.load_userdict(filepath)
            self.custom_dict = filepath

    def import_file(self, filepath, text_column=None):
        """
        导入文件（支持Excel/CSV/TXT）
        :param filepath: 文件路径
        :param text_column: 对于表格文件，指定文本所在列名或索引
        :return: 提取的文本内容
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError("文件不存在: {}".format(filepath))

        ext = os.path.splitext(filepath)[1].lower()
        content = ""

        try:
            if ext in ['.xlsx', '.xls']:
                content = self._read_excel(filepath, text_column)
            elif ext == '.csv':
                content = self._read_csv(filepath, text_column)
            elif ext == '.txt':
                content = self._read_txt(filepath)
            else:
                raise ValueError("不支持的文件格式: {}".format(ext))
        except Exception as e:
            raise Exception("读取文件失败: {}".format(e))

        self.text_content = content
        return content

    def _read_excel(self, filepath, text_column=None):
        """读取Excel文件"""
        df = pd.read_excel(filepath)

        if text_column is not None:
            if isinstance(text_column, int):
                content = ' '.join(df.iloc[:, text_column].astype(str).tolist())
            else:
                content = ' '.join(df[text_column].astype(str).tolist())
        else:
            # 默认合并所有列
            content = ' '.join(df.astype(str).values.flatten())

        return content

    def _read_csv(self, filepath, text_column=None):
        """读取CSV文件"""
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None

        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                break
            except:
                continue

        if df is None:
            raise Exception("无法识别CSV文件编码")

        if text_column is not None:
            if isinstance(text_column, int):
                content = ' '.join(df.iloc[:, text_column].astype(str).tolist())
            else:
                content = ' '.join(df[text_column].astype(str).tolist())
        else:
            content = ' '.join(df.astype(str).values.flatten())

        return content

    def _read_txt(self, filepath):
        """读取TXT文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        content = None

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except:
                continue

        if content is None:
            raise Exception("无法识别TXT文件编码")

        return content

    def clean_text(self, text=None, remove_punctuation=True, remove_numbers=True,
                   remove_spaces=True, remove_english=False, lowercase=True):
        """
        清洗文本
        :param text: 待清洗文本，默认使用已导入的文本
        :param remove_punctuation: 是否去除标点符号
        :param remove_numbers: 是否去除数字
        :param remove_spaces: 是否去除多余空格
        :param remove_english: 是否去除英文
        :param lowercase: 是否转为小写
        :return: 清洗后的文本
        """
        if text is None:
            text = self.text_content

        if not text:
            return ""

        # 转为小写
        if lowercase:
            text = text.lower()

        # 去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', text)

        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)

        # 去除邮箱
        text = re.sub(r'\S+@\S+', ' ', text)

        # 去除数字
        if remove_numbers:
            text = re.sub(r'\d+', ' ', text)

        # 去除英文（可选）
        if remove_english:
            text = re.sub(r'[a-zA-Z]+', ' ', text)

        # 去除标点符号
        if remove_punctuation:
            # 中文标点
            text = re.sub(r'[\s+\.\/_,$%^*()+\"\'\\]+', ' ', text)
            text = re.sub(r'[+——！，。？、~@#￥%……&*（）：；《》「」【】]+', ' ', text)
            # 保留中文字符、英文字符和空格
            # text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', text)

        # 去除多余空格
        if remove_spaces:
            text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def segment_text(self, text=None, use_jieba=True, cut_all=False, HMM=True):
        """
        分词处理
        :param text: 待分词文本，默认使用已导入的文本
        :param use_jieba: 是否使用jieba分词
        :param cut_all: 是否全模式分词
        :param HMM: 是否使用HMM模型
        :return: 分词结果列表
        """
        if text is None:
            text = self.text_content

        if not text:
            return []

        if use_jieba:
            # 使用jieba分词
            seg_list = jieba.cut(text, cut_all=cut_all, HMM=HMM)
            words = [w.strip() for w in seg_list if w.strip()]
        else:
            # 简单按空格分词
            words = text.split()

        # 过滤停用词
        words = [w for w in words if w not in self.stopwords and len(w) > 1]

        return words

    def get_word_frequency(self, words=None, top_n=100):
        """
        统计词频
        :param words: 分词结果列表，默认重新分词
        :param top_n: 返回前N个高频词
        :return: 词频字典 {词: 频次}
        """
        if words is None:
            words = self.segment_text()

        counter = Counter(words)
        self.word_freq = dict(counter.most_common(top_n))
        return self.word_freq

    def get_wordcloud_text(self, words=None):
        """
        生成适合wordcloud库的文本格式
        :param words: 分词结果列表
        :return: 空格分隔的词语字符串
        """
        if words is None:
            words = self.segment_text()
        return ' '.join(words)

    def get_wordcloud_frequencies(self, top_n=200):
        """
        生成适合wordcloud库的词频格式
        :param top_n: 返回前N个高频词
        :return: 词频字典
        """
        return self.get_word_frequency(top_n=top_n)

    def batch_import(self, filepaths, text_column=None):
        """
        批量导入文件
        :param filepaths: 文件路径列表
        :param text_column: 文本所在列
        :return: 合并后的文本内容
        """
        all_content = []

        for filepath in filepaths:
            try:
                content = self.import_file(filepath, text_column)
                all_content.append(content)
            except Exception as e:
                print("导入文件 {} 失败: {}".format(filepath, e))

        self.text_content = ' '.join(all_content)
        return self.text_content


class BatchProcessor(object):
    """批量处理器"""

    def __init__(self, data_processor):
        self.dp = data_processor
        self.results = []

    def process_batch(self, filepaths, output_dir, wordcloud_config=None, text_column=None):
        """
        批量处理文件生成词云
        :param filepaths: 文件路径列表
        :param output_dir: 输出目录
        :param wordcloud_config: 词云配置参数
        :param text_column: 文本所在列
        :return: 处理结果列表
        """
        import os
        from Utils.new_wordcloud import MyWordCloud

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.results = []

        for i, filepath in enumerate(filepaths):
            try:
                # 导入并处理文本
                self.dp.import_file(filepath, text_column)
                cleaned_text = self.dp.clean_text()
                words = self.dp.segment_text(cleaned_text)
                word_freq = self.dp.get_word_frequency(words, top_n=200)

                # 生成词云
                wc = MyWordCloud()
                config = wordcloud_config or {}

                wordcloud = wc.GenWordCloud(
                    seg_list=word_freq,
                    font_path=config.get('font_path'),
                    background_color=config.get('background_color', 'white'),
                    width=config.get('width', 800),
                    height=config.get('height', 600),
                    flag=0
                )

                # 保存结果
                filename = os.path.splitext(os.path.basename(filepath))[0]
                output_path = os.path.join(output_dir, "{}_wordcloud.png".format(filename))
                wordcloud.to_file(output_path)

                self.results.append({
                    'input': filepath,
                    'output': output_path,
                    'status': 'success',
                    'word_count': len(words),
                    'unique_words': len(word_freq)
                })

            except Exception as e:
                self.results.append({
                    'input': filepath,
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })

        return self.results


if __name__ == "__main__":
    # 测试代码
    dp = DataProcessor()
    dp.load_stopwords()

    # 测试文本清洗
    test_text = "这是一个测试文本！Hello World 123，包含数字和标点符号。http://example.com"
    cleaned = dp.clean_text(test_text)
    print("清洗后:", cleaned)

    # 测试分词
    words = dp.segment_text(cleaned)
    print("分词结果:", words)

    # 测试词频统计
    freq = dp.get_word_frequency(words, top_n=10)
    print("词频统计:", freq)
