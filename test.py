# coding=utf-8
from splinter import Browser
import time

browser = Browser('firefox')

browser.visit('https://www.amazon.co.jp/login')

email_input_field = browser.find_by_id('ap_email')
password_input_field = browser.find_by_id('ap_password')
submit_button = browser.find_by_id('signInSubmit')

email_input_field.fill('juteng2005@gmail.com')
password_input_field.fill('Juteng378084190')
submit_button.click()

browser.find_link_by_href('/gp/gc/ref=nav_cs_gc').click()
browser.find_link_by_text(unicode('残高・利用履歴', 'utf8')).click()

table = browser.find_by_css('table.gcYAData')[0]

trs = table.find_by_tag('tr')

print len(trs)

d=""
c=""

for tr in trs:
    tds = tr.find_by_tag('td')
    if not tds:
        continue
    recent_charge_date = tds[0].value
    recent_charge_code = tds[1].value

    if recent_charge_code.find(unicode('登録','utf8')) != -1:
        d = recent_charge_date
        c = recent_charge_code
        break


print d
print c

if d!="" and c!="":
    nostr=c[-5:-1]
    print nostr

    if nostr=="5E5Y":
        print 'nostr yes'
    else:
        print 'no'



