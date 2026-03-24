# WordCloud GUI v2.0

智能词云生成桌面工具 - 支持多数据源导入、文本清洗、词频分析和批量处理

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![wxPython](https://img.shields.io/badge/wxPython-4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 功能特性

### 核心功能
- **多数据源导入**：支持 TXT / CSV / Excel 文件批量导入
- **智能文本清洗**：自动去除停用词、标点符号、数字、特殊字符
- **中英文分词**：基于 jieba 分词，支持自定义词典
- **词云生成**：丰富的样式配置，支持自定义字体、背景色、形状
- **词频分析**：自动生成词频 TOP20 柱状图
- **批量处理**：支持批量导入多个文件，批量生成词云

### 导出功能
- **多格式导出**：PNG / JPG / PDF / SVG 格式
- **高清导出**：支持自定义分辨率（DPI）
- **报告生成**：自动生成词云分析报告（PDF / Markdown）

### 界面特性
- **跨平台支持**：Windows / macOS / Linux
- **主题切换**：亮色 / 暗色主题
- **现代化UI**：优化的用户界面和操作流程
- **实时预览**：调整参数后可实时预览词云效果

## 安装说明

### 环境要求
- Python 3.6+
- wxPython 4.0+
- 其他依赖库

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/wordcloud_gui.git
cd wordcloud_gui

# 安装依赖
pip install -r requirements.txt
```

### 依赖列表

```
wxPython>=4.0.0
wordcloud>=1.8.0
jieba>=0.42.0
pandas>=1.0.0
matplotlib>=3.0.0
Pillow>=8.0.0
numpy>=1.19.0
reportlab>=3.5.0
openpyxl>=3.0.0
```

## 快速开始

### 启动程序

```bash
python Main.py
```

### 基本使用流程

1. **导入数据**
   - 点击「数据导入」页面
   - 选择要导入的文件（支持 TXT / CSV / Excel）
   - 配置文本清洗选项
   - 点击「开始导入」

2. **生成词云**
   - 切换到「文本词云生成」页面
   - 选择字体、设置尺寸和颜色
   - 点击「词云生成」

3. **词频分析**
   - 切换到「词频分析」页面
   - 查看词频统计图表
   - 导出词频列表

4. **批量处理**
   - 切换到「批量处理」页面
   - 添加多个文件
   - 配置输出选项
   - 开始批量生成

## 功能详解

### 1. 数据导入

支持多种文件格式：
- **TXT文件**：纯文本文件，自动识别编码（UTF-8 / GBK / GB2312）
- **CSV文件**：支持自定义分隔符和文本列
- **Excel文件**：支持 .xlsx 和 .xls 格式

文本清洗选项：
- 去除标点符号
- 去除数字
- 去除多余空格
- 转为小写
- 自定义停用词表
- 自定义分词词典

### 2. 词云生成

配置选项：
- **字体选择**：支持系统中安装的 TTF 字体
- **尺寸设置**：自定义宽度和高度
- **背景颜色**：支持颜色选择器
- **字体大小**：设置最大/最小字体
- **蒙版形状**：支持自定义轮廓图片（可选）

### 3. 词频分析

可视化功能：
- 词频柱状图（水平/垂直）
- 多种颜色方案
- 支持导出图表

统计信息：
- 总词数
- 唯一词数
- 平均词频

### 4. 批量处理

批量操作：
- 同时处理多个文件
- 统一配置输出格式
- 显示处理进度
- 生成处理日志

## 跨平台说明

### Windows
- 支持 Windows 7/8/10/11
- 推荐使用 Python 3.8+

### macOS
- 支持 macOS 10.14+
- 需要安装 Xcode Command Line Tools
- 使用 Homebrew 安装 Python：
  ```bash
  brew install python
  ```

### Linux
- 支持 Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- 需要安装 GTK 开发库：
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev python3-pip libgtk-3-dev

  # CentOS/RHEL
  sudo yum install python3-devel gtk3-devel
  ```

## 常见问题

### 1. 中文显示乱码
**原因**：缺少中文字体

**解决方案**：
- 将中文字体文件（.ttf）放入 `data/font/` 目录
- 推荐字体：思源黑体、微软雅黑、SimHei

### 2. 导入Excel文件失败
**原因**：缺少 openpyxl 库

**解决方案**：
```bash
pip install openpyxl
```

### 3. 导出PDF失败
**原因**：缺少 reportlab 库

**解决方案**：
```bash
pip install reportlab
```

### 4. macOS 上界面显示异常
**原因**：wxPython 版本问题

**解决方案**：
```bash
pip install --upgrade wxPython
```

### 5. Linux 上无法启动
**原因**：缺少 GTK 依赖

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install libsdl2-2.0-0 libnotify4

# 如果仍有问题，尝试安装完整依赖
sudo apt-get install libgtk-3-dev libwebkitgtk-3.0-dev
```

## 目录结构

```
wordcloud_gui/
├── Main.py                 # 主程序入口
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── MyUI/                  # UI模块
│   ├── __init__.py
│   ├── MainFrame.py       # 主窗口框架
│   ├── MyNormal.py        # 格式文件词云
│   ├── MyText.py          # 文本词云生成
│   ├── MyWeb.py           # 网页文件词云
│   ├── MyDataImport.py    # 数据导入（新增）
│   ├── MyWordFreq.py      # 词频分析（新增）
│   ├── MyBatch.py         # 批量处理（新增）
│   ├── MyHelp.py          # 使用帮助
│   ├── MyAbout.py         # 关于软件
│   └── images.py          # 图像资源
├── Utils/                 # 工具模块
│   ├── __init__.py
│   ├── gl.py              # 全局变量
│   ├── new_wordcloud.py   # 词云生成
│   ├── cleaner.py         # HTML清洗
│   ├── data_processor.py  # 数据处理（新增）
│   ├── visualizer.py      # 可视化（新增）
│   └── exporter.py        # 导出模块（新增）
├── data/                  # 数据目录
│   ├── font/              # 字体文件
│   ├── stopwords/         # 停用词表
│   └── .catch/            # 缓存目录
├── bitmaps/               # 图标资源
├── img/                   # 图片资源
└── Doc/                   # 文档
    ├── about.txt
    └── help.txt
```

## 更新日志

### v2.0.0 (2024-03)
- 新增数据导入功能（支持 Excel/CSV/TXT）
- 新增文本清洗功能
- 新增词频分析可视化
- 新增批量处理功能
- 新增多格式导出（PNG/JPG/PDF/SVG）
- 新增报告生成功能
- 新增暗色/亮色主题切换
- 优化跨平台兼容性
- 重构UI界面

### v1.0.0 (2016-01)
- 初始版本发布
- 基础词云生成功能
- 支持文本文件导入

## 开源协议

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

- 作者：Tacey Wong
- 邮箱：your.email@example.com
- 项目主页：https://github.com/yourusername/wordcloud_gui

## 致谢

- [wordcloud](https://github.com/amueller/word_cloud) - 词云生成库
- [jieba](https://github.com/fxsjy/jieba) - 中文分词库
- [wxPython](https://wxpython.org/) - GUI框架
- [pandas](https://pandas.pydata.org/) - 数据处理库
- [matplotlib](https://matplotlib.org/) - 可视化库
