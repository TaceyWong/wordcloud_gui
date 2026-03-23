# coding:utf-8

import os
import io
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any

from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class WordCloudExporter:
    
    SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'svg', 'pdf', 'bmp', 'tiff']
    
    def __init__(self):
        pass
    
    def export_image(self, wordcloud: WordCloud, 
                     filepath: str, 
                     dpi: int = 300,
                     quality: int = 95) -> bool:
        try:
            ext = os.path.splitext(filepath)[1].lower().replace('.', '')
            
            if ext == 'svg':
                return self._export_svg(wordcloud, filepath)
            elif ext == 'pdf':
                return self._export_pdf(wordcloud, filepath, dpi)
            else:
                return self._export_raster(wordcloud, filepath, dpi, quality)
        except Exception as e:
            print(f"导出失败: {str(e)}")
            return False
    
    def _export_raster(self, wordcloud: WordCloud, 
                       filepath: str, 
                       dpi: int = 300, 
                       quality: int = 95) -> bool:
        try:
            array = wordcloud.to_array()
            img = Image.fromarray(array)
            
            ext = os.path.splitext(filepath)[1].lower().replace('.', '')
            
            if ext in ['jpg', 'jpeg']:
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                img.save(filepath, quality=quality, dpi=(dpi, dpi))
            else:
                img.save(filepath, dpi=(dpi, dpi))
            
            return True
        except Exception as e:
            print(f"栅格图像导出失败: {str(e)}")
            return False
    
    def _export_svg(self, wordcloud: WordCloud, filepath: str) -> bool:
        try:
            array = wordcloud.to_array()
            height, width = array.shape[:2]
            
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
            ax.imshow(array, interpolation='bilinear')
            ax.axis('off')
            
            fig.savefig(filepath, format='svg', bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            
            return True
        except Exception as e:
            print(f"SVG导出失败: {str(e)}")
            return False
    
    def _export_pdf(self, wordcloud: WordCloud, filepath: str, dpi: int = 300) -> bool:
        try:
            array = wordcloud.to_array()
            height, width = array.shape[:2]
            
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
            ax.imshow(array, interpolation='bilinear')
            ax.axis('off')
            
            fig.savefig(filepath, format='pdf', bbox_inches='tight', pad_inches=0, dpi=dpi)
            plt.close(fig)
            
            return True
        except Exception as e:
            print(f"PDF导出失败: {str(e)}")
            return False
    
    def export_to_bytes(self, wordcloud: WordCloud, 
                        format: str = 'png',
                        dpi: int = 150) -> bytes:
        array = wordcloud.to_array()
        img = Image.fromarray(array)
        
        buf = io.BytesIO()
        
        if format.lower() in ['jpg', 'jpeg']:
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            img.save(buf, format='JPEG', quality=95, dpi=(dpi, dpi))
        else:
            img.save(buf, format=format.upper(), dpi=(dpi, dpi))
        
        buf.seek(0)
        return buf.getvalue()


class ReportGenerator:
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
    
    def generate_markdown_report(self,
                                 word_freq: List[Tuple[str, int]],
                                 wordcloud_path: str = None,
                                 chart_path: str = None,
                                 title: str = '词云分析报告',
                                 output_path: str = None,
                                 top_n: int = 20) -> str:
        report_lines = []
        
        report_lines.append(f"# {title}")
        report_lines.append("")
        report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        report_lines.append("## 词频统计")
        report_lines.append("")
        report_lines.append(f"总词数: {sum(freq for _, freq in word_freq)}")
        report_lines.append(f"不同词数: {len(word_freq)}")
        report_lines.append("")
        
        if wordcloud_path and os.path.exists(wordcloud_path):
            report_lines.append("## 词云图")
            report_lines.append("")
            rel_path = os.path.relpath(wordcloud_path, os.path.dirname(output_path) if output_path else self.base_dir)
            report_lines.append(f"![词云图]({rel_path})")
            report_lines.append("")
        
        if chart_path and os.path.exists(chart_path):
            report_lines.append("## 词频分布图")
            report_lines.append("")
            rel_path = os.path.relpath(chart_path, os.path.dirname(output_path) if output_path else self.base_dir)
            report_lines.append(f"![词频分布图]({rel_path})")
            report_lines.append("")
        
        report_lines.append(f"## 高频词 TOP{top_n}")
        report_lines.append("")
        report_lines.append("| 排名 | 词语 | 频次 |")
        report_lines.append("|:----:|:----:|:----:|")
        
        for i, (word, freq) in enumerate(word_freq[:top_n], 1):
            report_lines.append(f"| {i} | {word} | {freq} |")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("*本报告由 WordCloud-GUI 自动生成*")
        
        report_content = '\n'.join(report_lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def generate_pdf_report(self,
                            word_freq: List[Tuple[str, int]],
                            wordcloud: WordCloud = None,
                            chart_fig: Figure = None,
                            title: str = '词云分析报告',
                            output_path: str = None,
                            top_n: int = 20,
                            font_path: str = None) -> bool:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            if font_path and os.path.exists(font_path):
                font_name = os.path.splitext(os.path.basename(font_path))[0]
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    chinese_font = font_name
                except:
                    chinese_font = 'Helvetica'
            else:
                chinese_font = 'Helvetica'
            
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=chinese_font,
                fontSize=18,
                alignment=1
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=chinese_font,
                fontSize=14
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=chinese_font,
                fontSize=10
            )
            
            story = []
            
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.5*cm))
            
            story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            story.append(Paragraph("词频统计", heading_style))
            story.append(Paragraph(f"总词数: {sum(freq for _, freq in word_freq)}", normal_style))
            story.append(Paragraph(f"不同词数: {len(word_freq)}", normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            if wordcloud:
                story.append(Paragraph("词云图", heading_style))
                wc_bytes = WordCloudExporter().export_to_bytes(wordcloud, 'png', dpi=150)
                wc_img = Image(io.BytesIO(wc_bytes), width=15*cm, height=10*cm)
                story.append(wc_img)
                story.append(Spacer(1, 0.5*cm))
            
            if chart_fig:
                story.append(Paragraph("词频分布图", heading_style))
                chart_buf = io.BytesIO()
                chart_fig.savefig(chart_buf, format='png', dpi=150, bbox_inches='tight')
                chart_buf.seek(0)
                chart_img = Image(chart_buf, width=15*cm, height=8*cm)
                story.append(chart_img)
                story.append(Spacer(1, 0.5*cm))
            
            story.append(Paragraph(f"高频词 TOP{top_n}", heading_style))
            
            table_data = [['排名', '词语', '频次']]
            for i, (word, freq) in enumerate(word_freq[:top_n], 1):
                table_data.append([str(i), word, str(freq)])
            
            table = Table(table_data, colWidths=[2*cm, 6*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("本报告由 WordCloud-GUI 自动生成", normal_style))
            
            doc.build(story)
            return True
            
        except ImportError:
            print("reportlab 未安装，无法生成 PDF 报告")
            return False
        except Exception as e:
            print(f"PDF 报告生成失败: {str(e)}")
            return False
    
    def generate_html_report(self,
                             word_freq: List[Tuple[str, int]],
                             wordcloud_path: str = None,
                             chart_path: str = None,
                             title: str = '词云分析报告',
                             output_path: str = None,
                             top_n: int = 20) -> str:
        import base64
        
        html_lines = []
        
        html_lines.append('<!DOCTYPE html>')
        html_lines.append('<html lang="zh-CN">')
        html_lines.append('<head>')
        html_lines.append('<meta charset="UTF-8">')
        html_lines.append(f'<title>{title}</title>')
        html_lines.append('<style>')
        html_lines.append('body { font-family: "Microsoft YaHei", Arial, sans-serif; margin: 40px; background: #f5f5f5; }')
        html_lines.append('.container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }')
        html_lines.append('h1 { text-align: center; color: #333; }')
        html_lines.append('h2 { color: #444; border-bottom: 2px solid #3498db; padding-bottom: 10px; }')
        html_lines.append('table { width: 100%; border-collapse: collapse; margin: 20px 0; }')
        html_lines.append('th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }')
        html_lines.append('th { background: #3498db; color: white; }')
        html_lines.append('tr:nth-child(even) { background: #f9f9f9; }')
        html_lines.append('tr:hover { background: #f1f1f1; }')
        html_lines.append('.stats { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }')
        html_lines.append('.image-container { text-align: center; margin: 20px 0; }')
        html_lines.append('.image-container img { max-width: 100%; border-radius: 5px; }')
        html_lines.append('.footer { text-align: center; color: #888; margin-top: 30px; font-size: 12px; }')
        html_lines.append('</style>')
        html_lines.append('</head>')
        html_lines.append('<body>')
        html_lines.append('<div class="container">')
        
        html_lines.append(f'<h1>{title}</h1>')
        html_lines.append(f'<p style="text-align: center; color: #666;">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        
        html_lines.append('<div class="stats">')
        html_lines.append(f'<strong>总词数:</strong> {sum(freq for _, freq in word_freq)} &nbsp;&nbsp;')
        html_lines.append(f'<strong>不同词数:</strong> {len(word_freq)}')
        html_lines.append('</div>')
        
        if wordcloud_path and os.path.exists(wordcloud_path):
            html_lines.append('<h2>词云图</h2>')
            html_lines.append('<div class="image-container">')
            with open(wordcloud_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            ext = os.path.splitext(wordcloud_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            html_lines.append(f'<img src="data:image/{ext};base64,{img_data}" alt="词云图">')
            html_lines.append('</div>')
        
        if chart_path and os.path.exists(chart_path):
            html_lines.append('<h2>词频分布图</h2>')
            html_lines.append('<div class="image-container">')
            with open(chart_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            ext = os.path.splitext(chart_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            html_lines.append(f'<img src="data:image/{ext};base64,{img_data}" alt="词频分布图">')
            html_lines.append('</div>')
        
        html_lines.append(f'<h2>高频词 TOP{top_n}</h2>')
        html_lines.append('<table>')
        html_lines.append('<tr><th>排名</th><th>词语</th><th>频次</th></tr>')
        
        for i, (word, freq) in enumerate(word_freq[:top_n], 1):
            html_lines.append(f'<tr><td>{i}</td><td>{word}</td><td>{freq}</td></tr>')
        
        html_lines.append('</table>')
        
        html_lines.append('<div class="footer">')
        html_lines.append('本报告由 WordCloud-GUI 自动生成')
        html_lines.append('</div>')
        
        html_lines.append('</div>')
        html_lines.append('</body>')
        html_lines.append('</html>')
        
        html_content = '\n'.join(html_lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content


if __name__ == "__main__":
    test_freq = [('Python', 100), ('Java', 80), ('JavaScript', 70), 
                 ('C++', 60), ('Go', 50), ('Rust', 40)]
    
    generator = ReportGenerator()
    md_report = generator.generate_markdown_report(test_freq, title='测试报告')
    print("Markdown 报告生成完成")
    print(md_report[:500])
