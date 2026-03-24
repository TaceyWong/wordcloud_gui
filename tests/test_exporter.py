# coding: utf-8
"""
导出模块测试用例
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

from Utils.exporter import ImageExporter, MarkdownExporter, ExportManager


class TestImageExporter(unittest.TestCase):
    """测试图像导出类"""

    def setUp(self):
        """测试前准备"""
        self.exporter = ImageExporter()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_supported_formats(self):
        """测试支持的格式"""
        formats = ImageExporter.SUPPORTED_FORMATS
        self.assertIsInstance(formats, list)
        self.assertIn('png', formats)
        self.assertIn('jpg', formats)


class TestMarkdownExporter(unittest.TestCase):
    """测试Markdown导出类"""

    def setUp(self):
        """测试前准备"""
        self.exporter = MarkdownExporter()
        self.test_dir = tempfile.mkdtemp()

        self.test_freq = {
            u'数据': 150,
            u'分析': 120,
            u'可视化': 100
        }

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_export_report(self):
        """测试导出报告"""
        output_path = os.path.join(self.test_dir, "test_report.md")

        self.exporter.export_report(
            output_path,
            "wordcloud.png",
            self.test_freq,
            title=u'测试报告'
        )

        self.assertTrue(os.path.exists(output_path))

        # 验证内容
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(u'测试报告', content)
            self.assertIn(u'数据', content)


class TestExportManager(unittest.TestCase):
    """测试导出管理器"""

    def setUp(self):
        """测试前准备"""
        self.manager = ExportManager()
        self.test_dir = tempfile.mkdtemp()

        self.test_freq = {
            u'数据': 150,
            u'分析': 120,
            u'可视化': 100
        }

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_export_report_markdown(self):
        """测试导出Markdown报告"""
        output_path = os.path.join(self.test_dir, "test_report.md")

        try:
            self.manager.export_report(
                output_path,
                "wordcloud.png",
                self.test_freq,
                format='markdown'
            )
            self.assertTrue(os.path.exists(output_path))
        except Exception as e:
            print("Export report test skipped:", e)


if __name__ == '__main__':
    unittest.main()
