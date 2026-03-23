# coding:utf-8
"""
导出模块
支持多格式图片导出、PDF/Markdown报告生成
"""
import os
import io
from typing import List, Tuple, Dict, Optional, Union

import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class Exporter:
    """导出类，负责多格式导出和报告生成"""
    
    def __init__(self):
        self.temp_dir = os.path.join(os.path.dirname(__file__), '..', 'data', '.catch')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def export_wordcloud_image(self, wordcloud: WordCloud, save_path: str, format: str = 'png', dpi: int = 300) -> None:
        """导出词云图片"""
        format = format.lower()
        valid_formats = ['png', 'jpg', 'jpeg', 'pdf', 'svg']
        
        if format not in valid_formats:
            raise ValueError(f"不支持的格式: {format}，支持格式: {valid_formats}")
        
        if format == 'svg':
            self._export_to_svg(wordcloud, save_path)
        elif format == 'pdf':
            self._export_to_pdf(wordcloud, save_path, dpi)
        else:
            wordcloud.to_file(save_path)
    
    def _export_to_svg(self, wordcloud: WordCloud, save_path: str) -> None:
        """导出为SVG格式"""
        svg_text = wordcloud.to_svg()
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(svg_text)
    
    def _export_to_pdf(self, wordcloud: WordCloud, save_path: str, dpi: int = 300) -> None:
        """导出为PDF格式"""
        image = wordcloud.to_image()
        
        fig, ax = plt.subplots(figsize=(image.width / 100, image.height / 100), dpi=100)
        ax.imshow(image, interpolation='bilinear')
        ax.axis('off')
        
        plt.savefig(save_path, format='pdf', dpi=dpi, bbox_inches='tight', pad_inches=0)
        plt.close()
    
    def export_figure(self, fig: plt.Figure, save_path: str, format: str = 'png', dpi: int = 300) -> None:
        """导出matplotlib图表"""
        fig.savefig(save_path, format=format.lower(), dpi=dpi, bbox_inches='tight')
        plt.close(fig)
    
    def generate_markdown_report(self, word_freq: List[Tuple[str, int]], wordcloud_path: str, chart_path: Optional[str] = None, title: str = '词云分析报告', top_n: int = 20) -> str:
        """生成Markdown格式报告"""
        report_content = [
            f'# {title}',
            '',
            f'生成时间: {self._get_current_time()}',
            '',
            '## 词云图',
            '',
            f'![词云图]({wordcloud_path})',
            '',
            '## 词频统计',
            '',
        ]
        
        if chart_path:
            report_content.extend([
                '### 词频分布图',
                '',
                f'![词频分布图]({chart_path})',
                '',
            ])
        
        report_content.extend([
            '### 高频词列表',
            '',
            '| 排名 | 词汇 | 词频 |',
            '|------|------|------|',
        ])
        
        for i, (word, freq) in enumerate(word_freq[:top_n], 1):
            report_content.append(f'| {i} | {word} | {freq} |')
        
        report_content.extend([
            '',
            '## 统计摘要',
            '',
            f'- 总词汇数: {len(word_freq)}',
            f'- 最高词频: {word_freq[0][1]} ({word_freq[0][0]})' if word_freq else '',
            f'- 前{top_n}词汇累计词频: {sum(freq for _, freq in word_freq[:top_n])}',
            '',
        ])
        
        return '\n'.join(report_content)
    
    def save_markdown_report(self, report_content: str, save_path: str) -> None:
        """保存Markdown报告"""
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def generate_pdf_report(self, word_freq: List[Tuple[str, int]], wordcloud_image: Union[str, Image.Image], chart_image: Optional[Union[str, Image.Image]] = None, save_path: str = 'report.pdf', title: str = '词云分析报告', top_n: int = 20) -> None:
        """生成PDF格式报告"""
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.gridspec as gridspec
        
        with PdfPages(save_path) as pdf:
            fig = plt.figure(figsize=(12, 16))
            gs = gridspec.GridSpec(3, 2, figure=fig)
            
            fig.suptitle(title, fontsize=16, y=0.98)
            
            ax1 = fig.add_subplot(gs[0, :])
            if isinstance(wordcloud_image, str):
                wc_img = Image.open(wordcloud_image)
            else:
                wc_img = wordcloud_image
            ax1.imshow(wc_img)
            ax1.axis('off')
            ax1.set_title('词云图', fontsize=14)
            
            ax2 = fig.add_subplot(gs[1, :])
            words = [item[0] for item in word_freq[:top_n]]
            freqs = [item[1] for item in word_freq[:top_n]]
            bars = ax2.bar(words, freqs, color=plt.cm.viridis(np.linspace(0, 1, len(words))))
            ax2.set_title(f'词频统计TOP{top_n}', fontsize=14)
            ax2.tick_params(axis='x', rotation=45)
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{int(height)}', ha='center', va='bottom')
            
            ax3 = fig.add_subplot(gs[2, :])
            ax3.axis('off')
            table_data = [['排名', '词汇', '词频']]
            for i, (word, freq) in enumerate(word_freq[:top_n], 1):
                table_data.append([str(i), word, str(freq)])
            
            table = ax3.table(cellText=table_data,
                            cellLoc='center',
                            loc='center',
                            bbox=[0, 0, 1, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            
            plt.figtext(0.5, 0.01, f'生成时间: {self._get_current_time()}', 
                        ha='center', fontsize=10)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
    
    def export_batch(self, wordclouds: List[Tuple[str, WordCloud]], output_dir: str, format: str = 'png', dpi: int = 300) -> List[str]:
        """批量导出词云"""
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        for name, wc in wordclouds:
            save_path = os.path.join(output_dir, f'{name}.{format.lower()}')
            try:
                self.export_wordcloud_image(wc, save_path, format, dpi)
                saved_paths.append(save_path)
            except Exception as e:
                print(f"导出 {name} 失败: {str(e)}")
        
        return saved_paths
    
    def export_data(self, word_freq: List[Tuple[str, int]], save_path: str, format: str = 'csv') -> None:
        """导出词频数据"""
        import pandas as pd
        
        df = pd.DataFrame(word_freq, columns=['词汇', '词频'])
        
        if format.lower() == 'csv':
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
        elif format.lower() in ['xls', 'xlsx']:
            df.to_excel(save_path, index=False)
        else:
            raise ValueError(f"不支持的数据格式: {format}")
    
    @staticmethod
    def _get_current_time() -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
