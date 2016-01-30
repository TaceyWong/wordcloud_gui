#coding:utf-8
import win32com.client

"""
语音功能
"""
# print "\xc3\xbb\xd3\xd0\xd7\xa2\xb2\xe1\xc0\xe0".decode("gbk")
def speak(text):
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk.Speak(text)
