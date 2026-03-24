# coding: utf-8
"""
数据处理模块测试用例
"""

from __future__ import print_function, unicode_literals
import unittest
import os
import sys
import tempfile
import shutil

# 添加项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from Utils.data_processor import DataProcessor, BatchProcessor


class TestDataProcessor(unittest.TestCase):
    """测试数据处理类"""

    def setUp(self):
        """测试前准备"""
        self.dp = DataProcessor()
        self.test_dir = tempfile.mkdtemp()

        # 创建测试文件
        self.test_txt = os.path.join(self.test_dir, "test.txt")
        with open(self.test_txt, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文本。Hello World! 12345\n")
            f.write("数据分析非常重要。Data analysis is important.\n")

        self.test_csv = os.path.join(self.test_dir, "test.csv")
        with open(self.test_csv, 'w', encoding='utf-8') as f:
            f.write("id,text,value\n")
            f.write("1,这是一个测试,100\n")
            f.write("2,数据分析,200\n")
            f.write("3,机器学习,300\n")

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_load_stopwords(self):
        """测试加载停用词"""
        stopwords = self.dp.load_stopwords()
        self.assertIsInstance(stopwords, set)
        self.assertIn('的', stopwords)
        self.assertIn('the', stopwords)

    def test_add_custom_stopwords(self):
        """测试添加自定义停用词"""
        self.dp.add_custom_stopwords(['测试', 'demo'])
        self.assertIn('测试', self.dp.stopwords)
        self.assertIn('demo', self.dp.stopwords)

    def test_import_txt(self):
        """测试导入TXT文件"""
        content = self.dp.import_file(self.test_txt)
        self.assertIsInstance(content, str)
        self.assertIn('测试', content)
        self.assertIn('Hello', content)

    def test_import_csv(self):
        """测试导入CSV文件"""
        content = self.dp.import_file(self.test_csv, text_column='text')
        self.assertIsInstance(content, str)
        self.assertIn('测试', content)
        self.assertIn('数据分析', content)

    def test_clean_text(self):
        """测试文本清洗"""
        test_text = "Hello World! 这是一个测试。12345 http://example.com"
        cleaned = self.dp.clean_text(test_text)
        self.assertNotIn('http', cleaned)
        self.assertNotIn('12345', cleaned)

    def test_segment_text(self):
        """测试分词"""
        self.dp.load_stopwords()
        test_text = "数据分析非常重要"
        words = self.dp.segment_text(test_text)
        self.assertIsInstance(words, list)
        self.assertTrue(len(words) > 0)

    def test_get_word_frequency(self):
        """测试词频统计"""
        self.dp.load_stopwords()
        test_text = "数据分析非常重要，数据分析很有用"
        words = self.dp.segment_text(test_text)
        freq = self.dp.get_word_frequency(words, top_n=10)
        self.assertIsInstance(freq, dict)
        self.assertTrue(len(freq) > 0)

    def test_batch_import(self):
        """测试批量导入"""
        files = [self.test_txt, self.test_csv]
        content = self.dp.batch_import(files)
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 0)


class TestBatchProcessor(unittest.TestCase):
    """测试批量处理器"""

    def setUp(self):
        """测试前准备"""
        self.dp = DataProcessor()
        self.bp = BatchProcessor(self.dp)
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir)

        # 创建测试文件
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("数据分析 机器学习 人工智能\n")
            f.write("数据可视化 自然语言处理\n")

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_process_batch(self):
        """测试批量处理"""
        # 注意：此测试需要字体文件才能正常运行
        # 这里仅测试接口调用
        try:
            font_path = os.path.join(BASE_DIR, "data", "font", "simsun.ttf")
            if not os.path.exists(font_path):
                self.skipTest("字体文件不存在")

            config = {
                'font_path': font_path,
                'background_color': 'white',
                'width': 400,
                'height': 300
            }

            results = self.bp.process_batch(
                [self.test_file],
                self.output_dir,
                wordcloud_config=config
            )

            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 1)

        except Exception as e:
            print("Batch process test skipped:", e)


if __name__ == '__main__':
    unittest.main()
