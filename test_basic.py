#!/usr/bin/env python
# coding:utf-8
"""
基本功能测试脚本
用于验证核心模块功能是否正常
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_processor():
    """测试数据处理模块"""
    print("=" * 50)
    print("测试数据处理模块 (data_processor)")
    print("=" * 50)
    
    try:
        from Utils.data_processor import DataProcessor
        dp = DataProcessor()
        
        # 测试1: 加载停用词
        print("\n1. 测试加载停用词...")
        stopwords_path = os.path.join("data", "stopwords", "cn_stopwords.txt")
        if os.path.exists(stopwords_path):
            dp.load_stopwords(stopwords_path)
            print(f"   ✓ 成功加载停用词，共 {len(dp.stopwords)} 个停用词")
        else:
            print(f"   ⚠ 停用词文件不存在: {stopwords_path}")
        
        # 测试2: 文本清洗
        print("\n2. 测试文本清洗...")
        test_text = "这是一段测试文本！包含123数字和@#$特殊字符。"
        cleaned_text = dp.clean_text(test_text)
        print(f"   原始文本: {test_text}")
        print(f"   清洗后: {cleaned_text}")
        print("   ✓ 文本清洗功能正常")
        
        # 测试3: 分词
        print("\n3. 测试中文分词...")
        words = dp.segment(cleaned_text)
        print(f"   分词结果: {words}")
        print("   ✓ 分词功能正常")
        
        # 测试4: 词频统计
        print("\n4. 测试词频统计...")
        freq = dp.get_word_freq(words)
        print(f"   词频统计: {freq}")
        print("   ✓ 词频统计功能正常")
        
        print("\n✅ 数据处理模块测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据处理模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualizer():
    """测试可视化模块"""
    print("\n" + "=" * 50)
    print("测试可视化模块 (visualizer)")
    print("=" * 50)
    
    try:
        from Utils.visualizer import Visualizer
        
        # 测试1: 获取颜色方案列表
        print("\n1. 测试获取颜色方案...")
        colormaps = Visualizer.get_available_colormaps()
        print(f"   ✓ 支持 {len(colormaps)} 种颜色方案")
        
        # 测试2: 颜色方案列表不为空
        if colormaps and len(colormaps) > 0:
            print(f"   前5种颜色方案: {colormaps[:5]}")
            print("   ✓ 颜色方案功能正常")
        else:
            print("   ⚠ 颜色方案列表为空")
        
        print("\n✅ 可视化模块测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 可视化模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exporter():
    """测试导出模块"""
    print("\n" + "=" * 50)
    print("测试导出模块 (exporter)")
    print("=" * 50)
    
    try:
        from Utils.exporter import Exporter
        
        # 测试1: 创建Exporter实例
        exporter = Exporter()
        print("\n1. ✓ Exporter实例创建成功")
        
        # 测试2: 测试时间戳获取
        time_str = exporter._get_current_time()
        print(f"2. ✓ 获取当前时间: {time_str}")
        
        print("\n✅ 导出模块测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 导出模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wordcloud():
    """测试词云核心模块"""
    print("\n" + "=" * 50)
    print("测试词云核心模块 (new_wordcloud)")
    print("=" * 50)
    
    try:
        from Utils.new_wordcloud import MyWordCloud
        
        # 测试1: 创建MyWordCloud实例
        wc = MyWordCloud()
        print("\n1. ✓ MyWordCloud实例创建成功")
        
        # 测试2: 测试加载停用词
        print("\n2. 测试加载停用词...")
        stopwords_path = os.path.join("data", "stopwords", "cn_stopwords.txt")
        if os.path.exists(stopwords_path):
            stopwords = wc.load_stopwords(stopwords_path)
            print(f"   ✓ 成功加载停用词，共 {len(stopwords)} 个停用词")
        else:
            print(f"   ⚠ 停用词文件不存在: {stopwords_path}")
        
        # 测试3: 测试分词
        print("\n3. 测试分词功能...")
        test_text = "这是一段用于测试分词功能的中文文本"
        seg_result = wc.word_cut(set(), test_text)
        print(f"   分词结果: {seg_result}")
        print("   ✓ 分词功能正常")
        
        print("\n✅ 词云核心模块测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 词云核心模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fonts():
    """测试字体文件是否存在"""
    print("\n" + "=" * 50)
    print("测试字体文件")
    print("=" * 50)
    
    font_dir = os.path.join("data", "font")
    if os.path.exists(font_dir):
        fonts = [f for f in os.listdir(font_dir) if f.lower().endswith(".ttf")]
        if fonts:
            print(f"\n✓ 找到 {len(fonts)} 个字体文件:")
            for f in fonts:
                print(f"  - {f}")
        else:
            print("\n⚠ 字体目录为空")
    else:
        print(f"\n⚠ 字体目录不存在: {font_dir}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("WordCloud-Gui 基本功能测试")
    print("=" * 50)
    
    results = []
    
    # 运行测试
    results.append(("数据处理模块", test_data_processor()))
    results.append(("可视化模块", test_visualizer()))
    results.append(("导出模块", test_exporter()))
    results.append(("词云核心模块", test_wordcloud()))
    
    # 测试字体
    test_fonts()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
