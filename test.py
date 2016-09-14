from splinter import Browser
import time
browser = Browser('firefox')
browser.visit('http://www.baidu.com')
browser.find_by_id('kw').fill('123151')
time.sleep(3)
browser.reload()

