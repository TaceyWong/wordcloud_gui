#coding: utf-8

import os
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import jieba
import cStringIO
# stream = cStringIO.StringIO(GetMondrianData())
# return wx.ImageFromStream(stream)


class MyWordCloud(object):
    def __init__(self):
        self.stopwords = {}
        self.seg_list =[]
        self.m_wordcloud = None

    def StopWord(self,filename):
        # pass
        f = open(filename, 'r')
        line = f.readline().rstrip()#strip()
        while line:
            self.stopwords.setdefault(line, 0)
            self.stopwords[line.decode('utf-8')] = 1
            line = f.readline().rstrip()
        f.close()
        return self.stopwords


    def WordCut(self,stopwords, inputfile):
        # pass
        with open (inputfile) as f:

            text = f.readlines()
            text = r' '.join(text)

            seg_generator = jieba.cut(text)

            self.seg_list = [i for i in seg_generator if i not in stopwords]

            self.seg_list = [i for i in self.seg_list if i != u' ']

            self.seg_list = r' '.join(self.seg_list)

        return self.seg_list

    def GenWordCloud(self,
                     seg_list = None,
                     font_path=None,
                     background_color="black",
                     margin=5,
                     width=1800, height=800,flag=1):
        # pass
        self.m_wordcloud = WordCloud(font_path=font_path,
                              background_color=background_color,
                              margin=margin,
                              width=width,
                              height=height)
        if flag==0:
            self.m_wordcloud = self.m_wordcloud.generate_from_frequencies(seg_list)
        else :
            self.m_wordcloud = self.m_wordcloud.generate(seg_list)
        return self.m_wordcloud

    # def Show(self,wordcloud = self.m_wordcloud):
    #     # pass
    #     plt.figure()
    #     plt.imshow(wordcloud)
    #     plt.axis("off")
    #     plt.show()


if __name__ == "__main__":

    wc = MyWordCloud()
    m_wordcloud = WordCloud()
    m_wordcloud.generate()
    m_wordcloud.co



