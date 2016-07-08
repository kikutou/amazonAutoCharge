# coding=utf-8
from splinter import Browser
from flask import session


def test(url):
    browser = Browser('firefox')
    if session:
        print 'get session'
        opened = session['opened_window']
        # opened.close()
        print opened
        result = 'success'
        print 'session cleared'

    else:
        print 'no session'
        browser.visit(url)
        result = browser.windows.current
    print result

    return result

if __name__ == '__main__':
    result = test('http://www.google.co.jp/')
    print result