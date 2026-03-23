#!/usr/bin/env python
# coding:utf-8
"""
语法验证脚本
用于验证代码的语法正确性，不依赖外部包
"""
import ast
import os
import sys

def check_python_syntax(file_path):
    """检查Python文件的语法正确性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e.msg} (第{e.lineno}行)"
    except Exception as e:
        return False, f"错误: {str(e)}"

def scan_directory(directory):
    """扫描目录下的所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过一些不需要检查的目录
        if '__pycache__' in root:
            continue
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """主函数"""
    print("=" * 60)
    print("WordCloud-Gui 代码语法验证")
    print("=" * 60)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 要检查的关键文件和目录
    key_files = [
        'Main.py',
        'Utils/data_processor.py',
        'Utils/visualizer.py',
        'Utils/exporter.py',
        'Utils/new_wordcloud.py',
        'MyUI/MainFrame.py',
        'MyUI/MyEnhanced.py',
    ]
    
    results = []
    
    # 检查关键文件
    print("\n检查关键文件:")
    print("-" * 60)
    
    for rel_path in key_files:
        full_path = os.path.join(project_dir, rel_path)
        if os.path.exists(full_path):
            is_valid, error = check_python_syntax(full_path)
            status = "✓" if is_valid else "✗"
            results.append((rel_path, is_valid, error))
            if is_valid:
                print(f"{status} {rel_path}")
            else:
                print(f"{status} {rel_path}: {error}")
        else:
            print(f"? {rel_path}: 文件不存在")
    
    # 统计结果
    print("\n" + "-" * 60)
    valid_count = sum(1 for _, v, _ in results if v)
    total_count = len(results)
    
    print(f"\n检查结果: {valid_count}/{total_count} 文件语法正确")
    
    if valid_count == total_count:
        print("\n🎉 所有关键文件语法正确！")
        return 0
    else:
        print("\n⚠ 部分文件存在语法问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
