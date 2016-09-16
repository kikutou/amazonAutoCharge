# coding=utf-8
from splinter import Browser
import time
import os

os.environ['DISPLAY'] = ':1'

browser = Browser('firefox')

browser.visit('https://www.amazon.co.jp/login')
