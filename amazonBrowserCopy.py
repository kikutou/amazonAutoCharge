# coding=utf-8
from splinter import Browser
import time
from PIL import Image
import pytesseract
import urllib
from flask import session
import os
import BrowserSaver
from xvfbwrapper import Xvfb

#   Wang 2016/07/05
#   def amazon_login(browser, user_name, password, code):


def amazon_login(browser, user_name, password):

    """
    amazonに自動ログインして、パラメータのカードコードを入力し、チャージする。
    チャージした結果を返す。

    :param browser:ブラウザインスタンス
    :param user_name:ログインユーザネーム
    :param password:ログインパスワード
    :param code:ギフトカードコード
    :return:チャージ結果
    """

    # ログインページを開く
    url = 'https://www.amazon.co.jp/login'
    browser.visit(url)

    print 'visit ok'

    # ログインする
    email_input_field = browser.find_by_id('ap_email')
    password_input_field = browser.find_by_id('ap_password')
    submit_button = browser.find_by_id('signInSubmit')

    if email_input_field and password_input_field and submit_button:
        email_input_field.fill(user_name)
        password_input_field.fill(password)
        submit_button.click()
    else:

        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }

    print 'login ok'

    browser.driver.save_screenshot('your_screenshot.png')

    captcha_image_field = browser.find_by_id('auth-captcha-image')
    if captcha_image_field:
        print 'there is captcha picture in login'

        html_code = browser.html

        return {
            'code': 6,
            'message': '画像認証が失敗しました。',
            'htmlcode': html_code
        }
    else:
        print 'no captcha in login'
        print 'go to charge page'

        # チャージ画面に移動する
        # url1 = 'https://www.amazon.co.jp/gc/redeem/ref=gc_redeem_new_exp_DesktopRedirect'
        # url1 = 'https://www.amazon.co.jp/'
        # browser.visit(url1)
        gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')

        print gift_link

        if gift_link:
            gift_link.click()
        else:
            html_code = browser.html

            return {
                'code': 4,
                'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
                'htmlcode': html_code
            }

        charge_link = browser.find_link_by_text(unicode('アカウントに登録','utf8'))
        # charge_link = browser.find_link_by_href('/gp/css/gc/payment/ref=gc_lpt3_ttl_redm')
        if charge_link:
            charge_link.click()
        else:
            html_code = browser.html

            return {
                'code': 4,
                'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
                'htmlcode': html_code
            }

        print 'visit charge page ok'
        html_code = browser.html

        return {
            'code': 7,
            'message': "ユーザー登録成功しました",
            'htmlcode': html_code
        }


def amazon_captcha_check(browser, password, login_captcha):

    # ログイン画像認識があるかどうかチェックする
    captcha_image_field = browser.find_by_id('auth-captcha-image')

    password_input_field = browser.find_by_id('ap_password')
    captcha_input_field = browser.find_by_id('auth-captcha-guess')
    submit_button = browser.find_by_id('signInSubmit')

    captcha_get = amazon_captcha_input(browser, login_captcha, captcha_input_field, password, password_input_field, submit_button)


    if captcha_get is False:

        return {
            'code': 6,
            'message': '画像認証が失敗しました。',
            'htmlcode': captcha_image_field['src']
        }

    # ログイン状態をチェクする
    login_warning_message = browser.find_by_id('auth-warning-message-box')
    login_error_message = browser.find_by_id('auth-error-message-box')

    if login_warning_message or login_error_message:
        login_alert_text = browser.find_by_css('span.a-list-item')
        result = login_alert_text.value
        print result
        # time.sleep(9000)
        if result.find(unicode('メールアドレスまたはパスワードが正しくありません。','utf8')) != -1:

            html_code = browser.html

            return {
                'code': 2,
                'message': 'アカウントまたはパスワードが間違いました。',
                'htmlcode': html_code
            }
        elif result.find(unicode('お客様のアカウントを強力に保護するため、パスワードを再入力してから、下の画像に表示されている文字を入力してください。','utf8')) != -1\
                or result.find(unicode('画像に表示されている文字を半角で入力してください。','utf8')) != -1:

            html_code = browser.html

            return {
                'code': 6,
                'message': '画像認証が失敗しました。',
                'htmlcode': html_code
            }
    # time.sleep(9000)


    print 'go to charge page'

    # チャージ画面に移動する
    # url1 = 'https://www.amazon.co.jp/gc/redeem/ref=gc_redeem_new_exp_DesktopRedirect'
    # url1 = 'https://www.amazon.co.jp/'
    # browser.visit(url1)
    gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')

    print gift_link

    if gift_link:
        gift_link.click()
    else:
        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }

    charge_link = browser.find_link_by_text(unicode('アカウントに登録','utf8'))
    # charge_link = browser.find_link_by_href('/gp/css/gc/payment/ref=gc_lpt3_ttl_redm')
    if charge_link:
        charge_link.click()
    else:
        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }

    print 'visit charge page ok'
    html_code = browser.html

    return {
        'code': 7,
        'message': "ユーザー登録成功しました",
        'htmlcode': html_code
    }


# Wang 2016/07/06
def amazon_charge(browser, code):

    captcha_image_field = browser.find_by_css('img.gc-captcha-image')
    # チャージ画像認識があるかどうかチェックする
    if captcha_image_field:

        print 'captcha in charge page'

        captcha_input_field = browser.find_by_name('captchaInput')
        code_input_field = browser.find_by_id('gc-redemption-input')
        charge_button = browser.find_by_name('applytoaccount')

        amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code, code_input_field, charge_button)

    else:

        print 'no captcha in charge page'

        # time.sleep(1)

        code_input_field = browser.find_by_id('gc-redemption-input')
        charge_button = browser.find_by_name('applytoaccount')

        print 'begin to charge'

        if code_input_field and charge_button:

            print 'get charge field ok'

            # チャージする
            code_input_field.fill(code)
            charge_button.click()

        else:

            print 'fail to get charge field'

            print code_input_field
            print charge_button

            html_code = browser.html

            return {
                'code': 4,
                'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
                'htmlcode': html_code
            }

    # チャージが完了するまで待ち
    time.sleep(0.5)

    print 'wait for charge result'

    result_field = browser.find_by_css('h4.a-alert-heading')
    if result_field:
        result = result_field.value

        html_code = browser.html

        if result.find(unicode('ギフト券番号は無効です','utf8')) != -1:

            return {
                'code': 3,
                'message': result,
                'htmlcode': html_code
            }

        elif result.find(unicode('セキュリティ検証が無効です', 'utf8')) != -1:

            return {
                'code': 6,
                'message': "画像認証が失敗しました。",
                'htmlcode': html_code
            }

        else:

            return {
                'code': 1,
                'message': result,
                'htmlcode': html_code
            }

    else:
        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }


# Wang 2016/07/05
def amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code, code_input_field, confirm_button):
    try:

        # 画像認証がある場合、その画像のurlを取得する
        captchaSrc = captcha_image_field['src']

        # 画像をローカルにダウンロードする
        path = str(time.time()) + ".jpg"
        urllib.urlretrieve(captchaSrc, path)

        # 画像を文字に変更する
        image = Image.open(path)
        captcha = pytesseract.image_to_string(image).replace(" ", "").replace("　", "")
        print captcha

        if captcha == "":

            captcha = 'abck12'

            print 'captcha is empty'

            captcha_get = False

            return captcha_get
        else:
            captcha_get = True

        # ダウンロードされた画像ファイルを削除する
        os.remove(path)

        # 再ロ入力する
        if code_input_field and captcha_input_field and confirm_button:

            code_input_field.fill(code)
            captcha_input_field.fill(captcha)
            confirm_button.click()

        else:
            raise Exception('ログイン画像認証が失敗しました。')

        return captcha_get

    except:

        print 'some problem in captcha'

        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }


def amazon_captcha_input(browser, non_auto_captcha, captcha_input_field, code, code_input_field, confirm_button):
    try:

        captcha = non_auto_captcha
        print captcha

        if captcha == "":

            print 'captcha is empty'

            captcha_get = False

            return captcha_get
        else:
            captcha_get = True

        # ダウンロードされた画像ファイルを削除する
        # os.remove(path)

        # 再入力する
        if code_input_field and captcha_input_field and confirm_button:

            code_input_field.fill(code)
            captcha_input_field.fill(captcha)
            browser.driver.save_screenshot('browser_screenshot.png')
            confirm_button.click()

        else:
            raise Exception('ログイン画像認証が失敗しました。')

        return captcha_get

    except:

        print 'some problem in captcha'

        html_code = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }


# Wang 2016/07/05
def amazon_main(user_name, password, codes, login_captcha):

    # ブラウザを新規する
    # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")

    result = []
    # charge_result = {}
    # vdisplay = Xvfb()
    # vdisplay.start()

    if not login_captcha:

        # browser = Browser('firefox')
        browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",)
            # service_log_path="./",
            # desired_capabilities={
            #     'phantomjs.page.settings.userAgent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
            # },)

        for x in range(0,3):
            result = [amazon_login(browser, user_name, password)]
            print result[0]['code']

            if result[0]['code'] != 4:
                break

    else:

        browser_list = BrowserSaver.Browsers()
        browser = browser_list.get_browser(user_name)
        print browser

        result = [amazon_captcha_check(browser, password, login_captcha)]
        print result[0]['code']

    # 認証画像を解析ができない場合は、その画像を取って得意先に送信する
    if result[0]['code'] == 6:

        captcha_image_field = browser.find_by_id('auth-captcha-image')
        result[0]['htmlcode'] = captcha_image_field['src']

        login_captcha_data = [
            {
                'browser': browser,
                'message': '認証画面が得意先に送信する',
                'code': 0
            }
        ]
        result = result + login_captcha_data
        print result[1]

        return result

    elif result[0]['code'] == 7:
        # clear result
        del result[:]

        for code_string in codes:
            for z in range(0,5):
                # remove the element which 'code' == 4 and 6
                result[:] = [element for element in result if element.get('code') != 4]
                result[:] = [element for element in result if element.get('code') != 6]

                charge_result = amazon_charge(browser, code_string)
                result = result + [charge_result]
                print charge_result['code']

                # if charge_result['code'] != 4:
                #     break
                if charge_result['code'] == 4:
                    pass
                elif charge_result['code'] == 6:
                    continue
                else:
                    break

            # if charge_result['code'] == 6:
            #
            #     captcha_image_field = browser.find_by_css('img.gc-captcha-image')
            #     charge_result['htmlcode'] = captcha_image_field['src']
            #
            #     print 'Failed to read charge captcha'
            #     return charge_result

            print code_string
        browser.quit()
        print result
        # vdisplay.stop()
        return result
    else:
        browser.quit()
        # vdisplay.stop()
        return result




if __name__ == '__main__':

    data = [
        {
            'user_name': 'nightblizzard@sina.com',
            'password': 'sc07051989',
            'codes': ['code0', 'code1', 'code2', 'code3']
        },
        {
            'user_name': '512317052@qq.com',
            'password': 'sc0705198',
            'codes': ['hello']
        },
        # {
        #     'user_name': 'juteng2005@gmail.com',
        #     'password': 'Juteng378084190',
        #     'codes': ['solong']
        # },
    ]

    for record in data:
        result_array = amazon_main(record['user_name'], record['password'], record['codes'], 'auto')
        result_count = len(result_array)
        for result_key in range(0, result_count):
            print result_array[result_key]['code']

    """
    data = {
        'user_name': 'nightblizzard@sina.com',
        'password': 'sc07051989',
        'codes': 'hello'
    }

    print amazon_login_main(data['user_name'],data['password'],data['code'])
    """
