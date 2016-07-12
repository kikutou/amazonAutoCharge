# coding=utf-8
from splinter import Browser
from flask import session
import time
import os


def test(url):
    browser = Browser('firefox')
    browser.visit(url)
    # print browser.windows.current
    #
    # result = browser.windows.current
    #
    # return result


    # print 'start circle'
    # while True:
    #     time.sleep(3)
    #     print 'search session'
        # if session:
        #     break
    # print 'get session'
    # opened = session['data']
    # opened = session['opened_window']
    # opened.close()
    # print opened
    # browser.windows.current.close()
    # result = 'success'

    # if session:
    #     print 'has session'
    #     print session
    #     browser.windows.current = session['opened_window']
    #     browser.find_by_id('lst-ib').fill(url)
    #     result = 'input find success'
    #
    # else:
    #     print 'no session'
    #     browser.visit(url)
    #     result = browser.windows.current
    # print result
    result = 'input fail'
    while True:
        time.sleep(3)
        fileName = 'captchaFile.txt'
        if os.path.exists(fileName):
            print 'txt exist'
            result = open(fileName).read()
            browser.find_by_id('lst-ib').fill(result)
            break

    return result


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