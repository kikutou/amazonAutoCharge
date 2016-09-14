from splinter import Browser
import time
try:
    browser = Browser('firefox')
    browser.visit('http://www.baidu.com')
    raise Exception('error')
except:
    time.sleep(3)
    browser.quit()
