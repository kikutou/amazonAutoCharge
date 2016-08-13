# coding=utf-8
import time
import urllib
import os
import re
from splinter import Browser
from PIL import Image
import pytesseract
from xvfbwrapper import Xvfb
import BrowserSaver


def amazon_login(browser, email, password, login_captcha):

    """
    amazonに自動ログインして、パラメータのカードコードを入力し、チャージする。
    チャージした結果を返す。

    :param browser:ブラウザインスタンス
    :param email:ログインユーザemail
    :param password:ログインパスワード
    :param code:ギフトカードコード
    :param login_captcha:認証画面が表示される文字
    :return:チャージ結果
    """
    if login_captcha is False:

        # ログインページを開く
        url = 'https://www.amazon.co.jp/login'
        browser.visit(url)

        print 'visit ok'

        # ログインする
        email_input_field = browser.find_by_id('ap_email')
        password_input_field = browser.find_by_id('ap_password')
        submit_button = browser.find_by_id('signInSubmit')

        if email_input_field and password_input_field and submit_button:
            email_input_field.fill(email)
            password_input_field.fill(password)
            submit_button.click()

        else:

            browser.quit()

            return {
                'code': 4,
                'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            }

        print 'login ok'
        #browser.driver.save_screenshot('./your_screenshot.png')

        gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')

        if gift_link:

            # テスト用
            browser_list = BrowserSaver.Browsers()
            browser_list.set_browser(email, browser)

            return {
                'code': 7,
                'message': "ユーザー登録成功しました",
            }
        else:
            return amazon_login_fail_check(browser, password, login_captcha)
    else:
        return amazon_login_fail_check(browser, password, login_captcha)


def amazon_login_fail_check(browser, password, login_captcha):

    # ログイン画像認識があるかどうかチェックする
    captcha_image_field = browser.find_by_id('auth-captcha-image')
    if captcha_image_field:

        print 'there is captcha picture in login'

        password_input_field = browser.find_by_id('ap_password')
        captcha_input_field = browser.find_by_id('auth-captcha-guess')
        submit_button = browser.find_by_id('signInSubmit')

        if login_captcha is False:
            captcha_get = amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, password, password_input_field, submit_button)
        else:
            captcha_get = amazon_captcha_input(browser, login_captcha, captcha_input_field, password, password_input_field, submit_button)
            
        if captcha_get is False:

            return {
                'code': 8,
                'message': '画像が認証できない。',
                'captcha_src': captcha_image_field['src']
            }

    # ログイン状態をチェクする
    login_warning_message = browser.find_by_id('auth-warning-message-box')
    login_error_message = browser.find_by_id('auth-error-message-box')
    login_alert_window = browser.find_by_id('auth-alert-window')
    login_email_missing_alert = browser.find_by_id('auth-email-missing-alert')
    login_password_missing_alert = browser.find_by_id('auth-password-missing-alert')

    if login_warning_message or login_error_message or login_alert_window \
            or login_email_missing_alert or login_password_missing_alert:

        login_alert_text = browser.find_by_css('span.a-list-item')
        result = ''
        if login_alert_text:
            result = login_alert_text.value

        print result

        if result.find(unicode('お客様のアカウントを強力に保護するため、パスワードを再入力してから、下の画像に表示されている文字を入力してください。', 'utf8')) != -1\
                or result.find(unicode('画像に表示されている文字を半角で入力してください。', 'utf8')) != -1:

            return {
                'code': 6,
                'message': '画像認証が失敗しました。',
            }
        elif login_email_missing_alert\
                or login_password_missing_alert\
                or result.find(unicode('メールアドレスまたはパスワードが正しくありません。', 'utf8')) != -1\
                or result.find(unicode('パスワードの入力', 'utf8')) != -1\
                or result.find(unicode('Eメールアドレスまたは携帯電話番号を入力', 'utf8')) != -1\
                or result.find(unicode('パスワードが正しくありません', 'utf8')) != -1\
                or result.find(unicode('このEメールアドレスを持つアカウントが見つかりません', 'utf8')) != -1:

            return {
                'code': 2,
                'message': 'アカウントまたはパスワードが間違いました。',
            }

    print 'go to charge page'

    return {
        'code': 7,
        'message': "ユーザー登録成功しました",
    }


def view_amazon_charge(browser):

    # チャージ画面に移動する
    # url1 = 'https://www.amazon.co.jp/gc/redeem/ref=gc_redeem_new_exp_DesktopRedirect'
    # url1 = 'https://www.amazon.co.jp/'
    # browser.visit(url1)
    gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')
    if gift_link:
        gift_link.click()
    else:

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
        }

    charge_link = browser.find_link_by_text(unicode('アカウントに登録','utf8'))
    if charge_link:
        charge_link.click()
    else:

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
        }

    print 'visit charge page ok'


def amazon_charge(browser, code):

    captcha_image_field = browser.find_by_css('img.gc-captcha-image')

    html_code_before_charge = browser.html

    # チャージ画像認識があるかどうかチェックする
    if captcha_image_field:

        print 'captcha in charge page'

        captcha_input_field = browser.find_by_name('captchaInput')
        code_input_field = browser.find_by_id('gc-redemption-input')
        charge_button = browser.find_by_name('applytoaccount')

        amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code, code_input_field, charge_button)

    else:

        print 'no captcha in charge page'

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

            return {
                'code': 4,
                'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            }

    # チャージが完了するまで待ち
    time.sleep(0.5)

    print 'wait for charge result'

    result_field = browser.find_by_css('h4.a-alert-heading')
    if result_field:
        result = result_field.value

        if result.find(unicode('ギフト券番号は無効です','utf8')) != -1:

            html_code_after_charge = browser.html

            return {
                'code': 3,
                'message': result,
                'html_code_before_charge': html_code_before_charge,
                'html_code after_charge': html_code_after_charge
            }

        elif result.find(unicode('セキュリティ検証が無効です', 'utf8')) != -1:

            html_code_after_charge = browser.html

            return {
                'code': 6,
                'message': "画像認証が失敗しました。",
                'html_code_before_charge': html_code_before_charge,
                'html_code after_charge': html_code_after_charge
            }

        else:

            html_code_after_charge = browser.html

            return {
                'code': 1,
                'message': result,
                'html_code_before_charge': html_code_before_charge,
                'html_code after_charge': html_code_after_charge
            }

    else:

        html_code_after_charge = browser.html

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'html_code_before_charge': html_code_before_charge,
            'html_code after_charge': html_code_after_charge
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
        image.load()

        captcha = pytesseract.image_to_string(image).replace(" ", "").replace("　", "")

        captcha = re.sub('[^a-zA-Z0-9]', "", captcha)

        captcha_get = True

        print captcha

        if captcha == "":
            charge_captcha_change = browser.find_by_id('gc-redemption-form-heading').value

            if charge_captcha_change:
                captcha = 'ERROR'
            else:
                print 'captcha is empty'

                captcha_get = False

                return captcha_get

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

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
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

        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
        }


def change_captcha(email):

    browser = BrowserSaver.Browsers().get_browser(email)
    browser.find_by_id('auth-captcha-refresh-link').click()

    time.sleep(1)

    captcha_image_field = browser.find_by_id('auth-captcha-image')

    return captcha_image_field['src']


def amazon_login_main(email, password, login_captcha):

    # ブラウザを新規する
    # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")

    result = []
    # vdisplay = Xvfb()
    # vdisplay.start()

    if login_captcha is False:

        browser = Browser('firefox')
        #browser = Browser('phantomjs',
                          #user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")
        # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
        #     # service_log_path="./",
        #     desired_capabilities={
        #         'phantomjs.page.settings.userAgent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
        #     },)

        for x in range(0,3):
            result = [amazon_login(browser, email, password, False)]
            print result[0]['code']

            # 画像認証が失敗した場合は、もう二度と認証してみる
            if result[0]['code'] == 6:
                for y in range(0,2):
                    result = [amazon_login_fail_check(browser, password, False)]
                    if result[0]['code'] != 6:
                        break

            if result[0]['code'] != 4:
                break

    else:

        browser_list = BrowserSaver.Browsers()
        browser = browser_list.get_browser(email)

        result = [amazon_login(browser, email, password, login_captcha)]

    # 認証画像を解析ができない場合は、その画像を取って得意先に送信する
    if result[0]['code'] == 6 or result[0]['code'] == 8:

        captcha_image_field = browser.find_by_id('auth-captcha-image')

        result[0] = {
            "code": 8,
            "message": "画像が認証できない",
            "html_code": captcha_image_field['src']
        }

        login_captcha_data = [
            {
                'browser': browser,
                'message': '認証画面が得意先に送信する',
                'code': 0
            }
        ]
        result = result + login_captcha_data

        return result

    elif result[0]['code'] == 7:
        result = result + [browser]

        return result

    else:

        browser.quit()
        # vdisplay.stop()
        return result


def amazon_charge_main(browser, code):

    result = {}

    print 'チャージ開始...'

    for z in range(0,5):
        # remove the element which 'code' == 4 and 6
        # result[:] = [element for element in result if element.get('code') != 4]
        # result[:] = [element for element in result if element.get('code') != 6]

        result = amazon_charge(browser, code)

        print result['code']

        if result['code'] != 4 and result['code'] != 6:
            break

    print code

    # vdisplay.stop()
    return result


if __name__ == '__main__':

    data = [
        {
            'email': 'nightblizzard@sina.com',
            'password': 'sc07051989',
            'codes': ['code0', 'code1', 'code2', 'code3']
            #'email': 'juteng2005@gmail.com',
            #'password': 'Juteng378084190',
            #'codes': ['AQHPZDE8PRZDCMD', 'AQHZJSJQQGW7EYZ']
            #'codes': ['AQHPZDE8PRZDCMD', 'AQHZJSJQQGW7EGP']

        },
        # {
        #     'email': '512317052@qq.com',
        #     'password': 'sc0705198',
        #     'codes': ['hello']
        # },
        # {
        #     'email': 'juteng2005@gmail.com',
        #     'password': 'Juteng378084190',
        #     'codes': ['solong']
        # },
    ]

    result = []

    for record in data:
        login_result = amazon_login_main(record['email'], record['password'], False)
        if login_result[0]['code'] == 7:
            browser = BrowserSaver.Browsers().get_browser(record['email'])

            view_amazon_charge(browser)

            for code in record['codes']:

                charge_result = amazon_charge_main(browser, code)

                result = result + [charge_result]

                if charge_result['code'] == 1:
                    break

    result_count = len(result)
    for result_key in range(0, result_count):
        print result[result_key]['code']

    """
    data = {
        'email': 'nightblizzard@sina.com',
        'password': 'sc07051989',
        'codes': 'hello'
    }

    print amazon_login_main(data['email'],data['password'],data['code'])
    """
