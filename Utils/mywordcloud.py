#coding: utf-8
 
import os
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import jieba


stopwords = {}

def stopword(filename = ''):
    global stopwords
    f = open(filename, 'r')
    line = f.readline().rstrip()
    while line:
        stopwords.setdefault(line, 0)
        stopwords[line.decode('utf-8')] = 1
        line = f.readline().rstrip()
    f.close()
print u"开始构建停词表······"
stopword(filename = 'data/stopwords.txt')


print u"开始进行文本读取及分词······"
with open (u'data/资本论.txt') as f:

    text = f.readlines()
    text = r' '.join(text)

    seg_generator = jieba.cut(text)

    seg_list = [i for i in seg_generator if i not in stopwords]

    seg_list = [i for i in seg_list if i != u' ']

    seg_list = r' '.join(seg_list)


print u"开始生成词云······"
# 词云
# wordcloud = WordCloud(max_font_size=40, relative_scaling=.5)
wordcloud = WordCloud(font_path='font/hysj.ttf',    background_color="black",   margin=5, width=1800, height=800) 

wordcloud = wordcloud.generate(seg_list)
#画图

# wordcloud.save("test.png")
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()