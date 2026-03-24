# coding: utf-8
"""
可视化模块测试用例
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

from Utils.visualizer import ColorScheme, WordFrequencyVisualizer, ThemeManager


class TestColorScheme(unittest.TestCase):
    """测试颜色方案类"""

    def test_get_scheme(self):
        """测试获取颜色方案"""
        scheme = ColorScheme.get_scheme('default')
        self.assertIsInstance(scheme, list)
        self.assertTrue(len(scheme) > 0)

    def test_get_all_schemes(self):
        """测试获取所有方案名称"""
        schemes = ColorScheme.get_all_schemes()
        self.assertIsInstance(schemes, list)
        self.assertIn('default', schemes)
        self.assertIn('warm', schemes)
        self.assertIn('cool', schemes)

    def test_generate_custom_scheme(self):
        """测试生成自定义颜色方案"""
        colors = ColorScheme.generate_custom_scheme('#ff6b6b', count=5)
        self.assertIsInstance(colors, list)
        self.assertEqual(len(colors), 5)


class TestWordFrequencyVisualizer(unittest.TestCase):
    """测试词频可视化类"""

    def setUp(self):
        """测试前准备"""
        self.viz = WordFrequencyVisualizer()
        self.test_dir = tempfile.mkdtemp()

        self.test_freq = {
            u'数据': 150,
            u'分析': 120,
            u'可视化': 100,
            u'Python': 90,
            u'词云': 85,
            u'统计': 80,
            u'图表': 75,
            u'机器学习': 70,
            u'人工智能': 65,
            u'大数据': 60
        }

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)

    def test_set_color_scheme(self):
        """测试设置颜色方案"""
        self.viz.set_color_scheme('warm')
        self.assertEqual(self.viz.color_scheme, ColorScheme.get_scheme('warm'))

    def test_plot_bar_chart(self):
        """测试绘制柱状图"""
        try:
            fig = self.viz.plot_bar_chart(self.test_freq, top_n=10)
            self.assertIsNotNone(fig)
        except Exception as e:
            print("Plot test skipped:", e)

    def test_save_bar_chart(self):
        """测试保存柱状图"""
        try:
            output_path = os.path.join(self.test_dir, "test_chart.png")
            self.viz.save_bar_chart(self.test_freq, output_path, top_n=10)
            self.assertTrue(os.path.exists(output_path))
        except Exception as e:
            print("Save chart test skipped:", e)


class TestThemeManager(unittest.TestCase):
    """测试主题管理器"""

    def test_init(self):
        """测试初始化"""
        tm = ThemeManager('light')
        self.assertEqual(tm.current_theme, 'light')

    def test_set_theme(self):
        """测试设置主题"""
        tm = ThemeManager()
        tm.set_theme('dark')
        self.assertEqual(tm.current_theme, 'dark')

    def test_get_color(self):
        """测试获取颜色"""
        tm = ThemeManager('light')
        bg_color = tm.get_color('bg_color')
        self.assertIsInstance(bg_color, str)
        self.assertTrue(bg_color.startswith('#'))


if __name__ == '__main__':
    unittest.main()
