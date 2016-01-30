#coding:utf-8

import re

def clean_html(html_file):
    cl = re.compile(r'<[^>]+>',re.S)
    html_text = cl.sub(' ',html_file)
    return html_text