#coding=utf-8
from splinter import Browser
import time

def google_login(user_name, password, code):

    browser = Browser('firefox')

    url = 'https://accounts.google.com/ServiceLogin'

    browser.visit(url)

    browser.find_by_id('Email').fill(user_name)

    browser.find_by_id('next').click()

    browser.find_by_id('Passwd').fill(password)

    browser.find_by_id('signIn').click()

    url1 = 'https://play.google.com/store?hl=jp'

    browser.visit(url1)

    browser.find_by_css('button.id-no-menu-change').click()

    time.sleep(1)

    browser.find_by_css('input.redeem-input-text-box').fill(code)

    browser.find_by_id('id-redeem-ok-button').click()

    time.sleep(2)

    result = browser.find_by_css('div.redeem-invalid-code-msg').value

    browser.quit()

    return result


if __name__ == '__main__':

    data = {'user_name': 'wangrunbo921',
            'password': 'wfy04231993',
            'code': 'hello'}

    print google_login(data['user_name'],data['password'],data['code'])