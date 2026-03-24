# coding: utf-8
"""
导出模块
支持多格式导出（PNG/JPG/PDF/SVG）和报告生成
"""

from __future__ import print_function, unicode_literals
import os
import sys
import io
from datetime import datetime

from PIL import Image
import matplotlib.pyplot as plt

# 兼容Python 2/3
if sys.version_info[0] == 2:
    import cStringIO
    StringIO = cStringIO.StringIO
else:
    from io import BytesIO
    StringIO = BytesIO

# 可选依赖
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not available, PDF export will be limited")


class ImageExporter(object):
    """图像导出类"""

    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']

    def __init__(self):
        self.default_dpi = 300
        self.quality = 95

    def export(self, wordcloud_obj, output_path, format=None, width=None, height=None, dpi=None):
        """
        导出词云图像
        :param wordcloud_obj: WordCloud对象或PIL Image
        :param output_path: 输出路径
        :param format: 输出格式（自动识别）
        :param width: 输出宽度
        :param height: 输出高度
        :param dpi: 分辨率
        :return: 输出文件路径
        """
        if dpi is None:
            dpi = self.default_dpi

        # 获取图像
        if hasattr(wordcloud_obj, 'to_image'):
            img = wordcloud_obj.to_image()
        elif isinstance(wordcloud_obj, Image.Image):
            img = wordcloud_obj
        else:
            raise ValueError("Invalid wordcloud object")

        # 调整尺寸
        if width or height:
            orig_width, orig_height = img.size
            if width and height:
                new_size = (width, height)
            elif width:
                ratio = float(width) / orig_width
                new_size = (width, int(orig_height * ratio))
            else:
                ratio = float(height) / orig_height
                new_size = (int(orig_width * ratio), height)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 确定格式
        if format is None:
            ext = os.path.splitext(output_path)[1].lower().lstrip('.')
            if ext in ['jpg', 'jpeg']:
                format = 'JPEG'
            elif ext == 'png':
                format = 'PNG'
            elif ext == 'bmp':
                format = 'BMP'
            elif ext in ['tiff', 'tif']:
                format = 'TIFF'
            elif ext == 'webp':
                format = 'WEBP'
            else:
                format = 'PNG'

        # 处理JPEG格式（需要RGB模式）
        if format.upper() in ['JPEG', 'JPG'] and img.mode in ('RGBA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # 保存图像
        save_kwargs = {'dpi': (dpi, dpi)}
        if format.upper() in ['JPEG', 'JPG', 'WEBP']:
            save_kwargs['quality'] = self.quality
            save_kwargs['optimize'] = True

        img.save(output_path, format=format, **save_kwargs)

        return output_path

    def export_hd(self, wordcloud_obj, output_path, scale=2):
        """
        高清导出
        :param wordcloud_obj: WordCloud对象
        :param output_path: 输出路径
        :param scale: 缩放倍数
        """
        img = wordcloud_obj.to_image()
        width, height = img.size
        new_size = (width * scale, height * scale)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        img.save(output_path, dpi=(self.default_dpi, self.default_dpi))
        return output_path


class SVGExporter(object):
    """SVG导出类"""

    def export(self, wordcloud_obj, output_path):
        """
        导出为SVG格式
        :param wordcloud_obj: WordCloud对象
        :param output_path: 输出路径
        """
        # wordcloud库本身支持SVG导出
        if hasattr(wordcloud_obj, 'to_svg'):
            svg_content = wordcloud_obj.to_svg()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return output_path
        else:
            raise ValueError("WordCloud object does not support SVG export")


class PDFExporter(object):
    """PDF导出类"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export")

        self.styles = getSampleStyleSheet()
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册常见中文字体
            font_paths = [
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
                'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux
                '/System/Library/Fonts/PingFang.ttc',  # macOS
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font_name = os.path.splitext(os.path.basename(font_path))[0]
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        self.chinese_font = font_name
                        break
                    except:
                        continue
            else:
                self.chinese_font = 'Helvetica'
        except:
            self.chinese_font = 'Helvetica'

    def export_image(self, image_path, output_path, title=None):
        """
        将图像导出为PDF
        :param image_path: 图像路径
        :param output_path: 输出PDF路径
        :param title: PDF标题
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 添加标题
        if title:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontName=self.chinese_font,
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 居中
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

        # 添加图像
        img = RLImage(image_path, width=6*inch, height=4*inch)
        img.hAlign = 'CENTER'
        story.append(img)

        doc.build(story)
        return output_path

    def export_report(self, output_path, wordcloud_image, word_freq, title=u'词云分析报告',
                      metadata=None):
        """
        导出词云分析报告
        :param output_path: 输出路径
        :param wordcloud_image: 词云图像路径
        :param word_freq: 词频字典
        :param title: 报告标题
        :param metadata: 元数据字典
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=20,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#2c3e50')
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=6
        )

        # 封面
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*inch))

        # 生成时间
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        story.append(Paragraph(u'生成时间: {}'.format(time_str), body_style))
        story.append(PageBreak())

        # 词云图
        story.append(Paragraph(u'一、词云图', heading_style))
        story.append(Spacer(1, 0.2*inch))

        if wordcloud_image and os.path.exists(wordcloud_image):
            img = RLImage(wordcloud_image, width=6*inch, height=4*inch)
            img.hAlign = 'CENTER'
            story.append(img)

        story.append(PageBreak())

        # 词频统计
        story.append(Paragraph(u'二、词频统计', heading_style))
        story.append(Spacer(1, 0.2*inch))

        # 创建词频表格
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]

        table_data = [[u'排名', u'词语', u'频次', u'占比']]
        total_freq = sum(word_freq.values())

        for i, (word, freq) in enumerate(sorted_words, 1):
            percentage = '{:.2f}%'.format(100.0 * freq / total_freq) if total_freq > 0 else '0.00%'
            table_data.append([str(i), word, str(freq), percentage])

        table = Table(table_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        story.append(table)

        # 元数据
        if metadata:
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(u'三、分析参数', heading_style))
            story.append(Spacer(1, 0.2*inch))

            meta_data = [[u'参数', u'值']]
            for key, value in metadata.items():
                meta_data.append([key, str(value)])

            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95a5a6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ]))
            story.append(meta_table)

        doc.build(story)
        return output_path


class MarkdownExporter(object):
    """Markdown报告导出类"""

    def export_report(self, output_path, wordcloud_image, word_freq, title=u'词云分析报告',
                      metadata=None):
        """
        导出Markdown格式报告
        :param output_path: 输出路径
        :param wordcloud_image: 词云图像路径（相对路径）
        :param word_freq: 词频字典
        :param title: 报告标题
        :param metadata: 元数据字典
        """
        lines = []

        # 标题
        lines.append('# {}'.format(title))
        lines.append('')
        lines.append('生成时间: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        lines.append('')

        # 词云图
        lines.append('## 一、词云图')
        lines.append('')
        if wordcloud_image:
            lines.append('![词云图]({})'.format(wordcloud_image))
        lines.append('')

        # 词频统计
        lines.append('## 二、词频统计')
        lines.append('')
        lines.append('| 排名 | 词语 | 频次 | 占比 |')
        lines.append('|------|------|------|------|')

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        total_freq = sum(word_freq.values())

        for i, (word, freq) in enumerate(sorted_words, 1):
            percentage = '{:.2f}%'.format(100.0 * freq / total_freq) if total_freq > 0 else '0.00%'
            lines.append('| {} | {} | {} | {} |'.format(i, word, freq, percentage))

        lines.append('')

        # 元数据
        if metadata:
            lines.append('## 三、分析参数')
            lines.append('')
            lines.append('| 参数 | 值 |')
            lines.append('|------|-----|')
            for key, value in metadata.items():
                lines.append('| {} | {} |'.format(key, value))
            lines.append('')

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return output_path


class ExportManager(object):
    """导出管理器"""

    def __init__(self):
        self.image_exporter = ImageExporter()
        self.svg_exporter = SVGExporter()
        self.markdown_exporter = MarkdownExporter()
        if REPORTLAB_AVAILABLE:
            self.pdf_exporter = PDFExporter()
        else:
            self.pdf_exporter = None

    def export_wordcloud(self, wordcloud_obj, output_path, format=None, **kwargs):
        """
        导出词云
        :param wordcloud_obj: WordCloud对象
        :param output_path: 输出路径
        :param format: 格式（png/jpg/pdf/svg等）
        :param kwargs: 其他参数
        """
        ext = os.path.splitext(output_path)[1].lower().lstrip('.')

        if ext == 'svg':
            return self.svg_exporter.export(wordcloud_obj, output_path)
        elif ext == 'pdf':
            if self.pdf_exporter:
                # 先导出为图片，再转为PDF
                temp_img = output_path.replace('.pdf', '_temp.png')
                self.image_exporter.export(wordcloud_obj, temp_img)
                result = self.pdf_exporter.export_image(temp_img, output_path)
                os.remove(temp_img)
                return result
            else:
                raise ImportError("reportlab is required for PDF export")
        else:
            return self.image_exporter.export(wordcloud_obj, output_path, format=format, **kwargs)

    def export_report(self, output_path, wordcloud_image, word_freq, title=u'词云分析报告',
                      metadata=None, format='pdf'):
        """
        导出分析报告
        :param output_path: 输出路径
        :param wordcloud_image: 词云图像路径
        :param word_freq: 词频字典
        :param title: 报告标题
        :param metadata: 元数据
        :param format: 格式（pdf/markdown）
        """
        if format.lower() == 'pdf':
            if self.pdf_exporter:
                return self.pdf_exporter.export_report(output_path, wordcloud_image, word_freq,
                                                       title, metadata)
            else:
                raise ImportError("reportlab is required for PDF export")
        elif format.lower() in ['md', 'markdown']:
            return self.markdown_exporter.export_report(output_path, wordcloud_image, word_freq,
                                                        title, metadata)
        else:
            raise ValueError("Unsupported report format: {}".format(format))


if __name__ == "__main__":
    # 测试代码
    print("支持的图像格式:", ImageExporter.SUPPORTED_FORMATS)

    # 测试Markdown导出
    test_freq = {
        u'数据': 150,
        u'分析': 120,
        u'可视化': 100,
        u'Python': 90,
        u'词云': 85
    }

    md_exporter = MarkdownExporter()
    md_exporter.export_report('test_report.md', 'wordcloud.png', test_freq)
    print("Markdown报告已导出到 test_report.md")
