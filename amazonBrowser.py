# coding=utf-8
from splinter import Browser
import time
from PIL import Image
import pytesseract
import urllib
import codecs
import os
import BrowserSaver
from xvfbwrapper import Xvfb


def amazon_login(browser, user_name, password, login_captcha):

    """
    amazonに自動ログインして、パラメータのカードコードを入力し、チャージする。
    チャージした結果を返す。

    :param browser:ブラウザインスタンス
    :param user_name:ログインユーザネーム
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

    return amazon_captcha_check(browser, password, login_captcha)


def amazon_captcha_check(browser, password, login_captcha):

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
                'htmlcode': captcha_image_field['src']
            }

    # ログイン状態をチェクする
    login_warning_message = browser.find_by_id('auth-warning-message-box')
    login_error_message = browser.find_by_id('auth-error-message-box')

    if login_warning_message or login_error_message:
        login_alert_text = browser.find_by_css('span.a-list-item')
        result = login_alert_text.value
        print result

        if result.find(unicode('メールアドレスまたはパスワードが正しくありません。','utf8')) != -1\
                or result.find(unicode('パスワードの入力','utf8')) != -1\
                or result.find(unicode('Eメールアドレスまたは携帯電話番号を入力','utf8')) != -1:

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


def create_status_text(txt):

    captcha_file = codecs.open('charge_status', 'w')
    captcha_file.write(txt)


def change_captcha(user_name):

    browser = BrowserSaver.Browsers().get_browser(user_name)
    browser.find_by_id('auth-captcha-refresh-link').click()

    time.sleep(1)

    captcha_image_field = browser.find_by_id('auth-captcha-image')

    return captcha_image_field['src']


def amazon_main(user_name, password, codes, login_captcha):

    create_status_text('送信しています...')

    # ブラウザを新規する
    # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")

    result = []
    # vdisplay = Xvfb()
    # vdisplay.start()

    if login_captcha is False:

        browser = Browser('firefox')
        # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
        #     # service_log_path="./",
        #     desired_capabilities={
        #         'phantomjs.page.settings.userAgent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
        #     },)
        create_status_text('登録中...')

        for x in range(0,3):
            result = [amazon_login(browser, user_name, password, False)]
            print result[0]['code']

            # 画像認証が失敗した場合は、もう二度と認証してみる
            if result[0]['code'] == 6:
                for y in range(0,2):
                    result = [amazon_captcha_check(browser, password, False)]
                    if result[0]['code'] != 6:
                        break

            if result[0]['code'] != 4:
                break

    else:

        browser_list = BrowserSaver.Browsers()
        browser = browser_list.get_browser(user_name)

        create_status_text('登録中...')
        result = [amazon_login(browser, user_name, password, login_captcha)]

    # 認証画像を解析ができない場合は、その画像を取って得意先に送信する
    if result[0]['code'] == 6 or result[0]['code'] == 8:

        captcha_image_field = browser.find_by_id('auth-captcha-image')

        result[0] = {
            "code": 8,
            "message": "画像が認証できない",
            "htmlcode": captcha_image_field['src']
        }

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

        create_status_text('登録成功、チャージ準備中...')
        time.sleep(1)

        # clear result
        del result[:]

        serial_number = 0
        for code_string in codes:

            serial_number += 1

            create_status_text('チャージ開始...')

            for z in range(0,5):
                # remove the element which 'code' == 4 and 6
                result[:] = [element for element in result if element.get('code') != 4]
                result[:] = [element for element in result if element.get('code') != 6]

                create_status_text('code' + str(serial_number) + ':' + code_string + '---' + 'チャージ中...')
                charge_result = amazon_charge(browser, code_string)
                result = result + [charge_result]
                print charge_result['code']

                if charge_result['code'] != 4 and charge_result['code'] != 6:
                    break

            print code_string
            create_status_text('code' + str(serial_number) + ':' + code_string + '---' + 'チャージ完了')
            time.sleep(1)

        create_status_text('チャージ完了、結果を準備中...')
        time.sleep(1)

        browser.quit()
        os.remove('charge_status')
        print result
        # vdisplay.stop()
        return result
    else:
        create_status_text('エラーが発生しました、チャージ失敗')
        time.sleep(1)
        browser.quit()
        os.remove('charge_status')
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
        result_array = amazon_main(record['user_name'], record['password'], record['codes'], False)
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
