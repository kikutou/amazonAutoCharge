# coding=utf-8
from splinter import Browser
from flask import session
import time
import os
import BrowserSaver



def test(url):
    browser = Browser('firefox')
    browser.visit(url)
    # window = browser.windows.current
    return browser

def input_test(text):
    window_list = BrowserSaver.Browsers()
    browser = window_list.get_browser('self_id')

    # browser.windows.current = window_list.get_browser('self_id')
    # print window_list.__browsers
    browser.find_by_id('lst-ib').fill(text)
    print window_list.get_browser('self_id')
    return 'input'

    # result = 'input fail'
    # while True:
    #     time.sleep(3)
    #     fileName = 'captchaFile.txt'
    #     if os.path.exists(fileName):
    #         print 'txt exist'
    #         result = open(fileName).read()
    #         browser.find_by_id('lst-ib').fill(result)
    #         break
    #
    # return result


def fill(window):
    print window
    browser = Browser('firefox')
    browser.windows.current = window
    print browser.windows.current
    print browser.find_by_id('lst-ib')
    browser.find_by_id('lst-ib').fill('input find success')

    return 'input find success'

# def cercle_text():



if __name__ == '__main__':
    result = test('http://www.google.co.jp/')
    print result