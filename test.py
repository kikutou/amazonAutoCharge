# coding=utf-8
from splinter import Browser
import time
import os
<<<<<<< HEAD

os.environ['DISPLAY'] = ':1'
=======
>>>>>>> 040763aac0ce569537b34486051e08b873845ef6

os.environ['DISPLAY'] = ':1'

browser = Browser('firefox')

browser.visit('https://www.amazon.co.jp/login')
