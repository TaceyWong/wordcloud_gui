# coding: utf-8
"""
测试运行脚本
"""

from __future__ import print_function, unicode_literals
import unittest
import sys
import os

# 添加项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def run_tests():
    """运行所有测试"""
    # 发现测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(BASE_DIR, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
