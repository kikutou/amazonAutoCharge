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
                'title': 'Amazon接続エラー',
                'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
            }

        print 'login ok'
        #browser.driver.save_screenshot('./your_screenshot.png')

        # gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')
        gift_link = browser.find_link_by_href('/gp/gc/ref=nav_cs_gc')

        if gift_link:

            # テスト用
            # browser_list = BrowserSaver.Browsers()
            # browser_list.set_browser(email, browser)

            return {
                'code': 7,
                'message': "ユーザー登録成功しました",
            }
        else:
            return amazon_login_fail_check(browser, password, login_captcha)
            # return amazon_login_fail_check(browser, password, login_captcha, email)
    else:
        return amazon_login_fail_check(browser, password, login_captcha)
        # return amazon_login_fail_check(browser, password, login_captcha, email)


def amazon_login_fail_check(browser, password, login_captcha):
# def amazon_login_fail_check(browser, password, login_captcha, email):

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
                'title': 'Amazonにログインできない',
                'message': 'Amazonへログインができないようです。'
                           'お客様が入力したアカウント・パスワードに問題があるか、'
                           'Amazonのログインに問題が発生している可能性があります。',
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
                'title': 'Amazonにログインできない',
                'message': 'Amazonへログインができないようです。'
                           'お客様が入力したアカウント・パスワードに問題があるか、'
                           'Amazonのログインに問題が発生している可能性があります。',
            }

    print 'go to charge page'

    # テスト用
    # browser_list = BrowserSaver.Browsers()
    # browser_list.set_browser(email, browser)

    return {
        'code': 7,
        'message': "ユーザー登録成功しました",
    }


def view_amazon_charge(browser):

    # チャージ画面に移動する
    # url1 = 'https://www.amazon.co.jp/gc/redeem/ref=gc_redeem_new_exp_DesktopRedirect'
    # url1 = 'https://www.amazon.co.jp/'
    # browser.visit(url1)
    # gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')
    gift_link = browser.find_link_by_href('/gp/gc/ref=nav_cs_gc')

    if gift_link:
        gift_link.click()
    else:
        browser.reload()
        gift_link = browser.find_link_by_href('/gp/gc/ref=nav_cs_gc')
        if gift_link:
            gift_link.click()
        else:
            return {
                'code': 25,
                'title': 'コード未入力エラー',
                'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
            }

    charge_link = browser.find_link_by_text(unicode('アカウントに登録','utf8'))
    if charge_link:
        charge_link.click()
    else:
        browser.reload()
        charge_link = browser.find_link_by_text(unicode('アカウントに登録', 'utf8'))
        if charge_link:
            charge_link.click()
        else:
            return {
                'code': 25,
                'title': 'コード未入力エラー',
                'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
            }

    print 'visit charge page ok'
    return


def amazon_charge(browser, code):

    captcha_image_field = browser.find_by_css('img.gc-captcha-image')

    html_code_before_charge = browser.html

    # チャージ画像認識があるかどうかチェックする
    if captcha_image_field:

        print 'captcha in charge page'

        captcha_input_field = browser.find_by_name('captchaInput')
        code_input_field = browser.find_by_id('gc-redemption-input')
        charge_button = browser.find_by_name('applytoaccount')

        input_result = amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code, code_input_field, charge_button)

        if input_result is not True:
            browser.reload()
            captcha_input_field = browser.find_by_name('captchaInput')
            code_input_field = browser.find_by_id('gc-redemption-input')
            charge_button = browser.find_by_name('applytoaccount')
            input_result = amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code, code_input_field, charge_button)
            if input_result is not True:
                return {
                    'code': 25,
                    'title': 'コード未入力エラー',
                    'message': "Amazonでチャージの手続きを行いましたが、レスポンスが返ってきません。チャージが正常に完了していない可能性があります。",
                }

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

            browser.reload()
            code_input_field = browser.find_by_id('gc-redemption-input')
            charge_button = browser.find_by_name('applytoaccount')
            captcha_input_field = browser.find_by_name('captchaInput')
            captcha_image_field = browser.find_by_css('img.gc-captcha-image')

            if not (code_input_field and charge_button):
                return {
                    'code': 25,
                    'title': 'コード未入力エラー',
                    'message': "Amazonでチャージの手続きを行いましたが、レスポンスが返ってきません。チャージが正常に完了していない可能性があります。",
                }
            else:
                if captcha_input_field and captcha_image_field:
                    input_result = amazon_captcha_auto_input(browser, captcha_image_field, captcha_input_field, code,
                                                             code_input_field, charge_button)
                    if input_result is not True:
                        return {
                            'code': 25,
                            'title': 'コード未入力エラー',
                            'message': "Amazonでチャージの手続きを行いましたが、レスポンスが返ってきません。チャージが正常に完了していない可能性があります。",
                        }
                else:
                    # チャージする
                    code_input_field.fill(code)
                    charge_button.click()

    # チャージが完了するまで待ち
    time.sleep(0.5)

    print 'wait for charge result'

    success_result_field = browser.find_by_id('alertRedemptionSuccess')
    success_account_field = browser.find_by_id('gc-redemption-success-summary')

    gift_charged_message = browser.find_by_id('gc-redemption-info-message')

    result_field = browser.find_by_css('h4.a-alert-heading')

    if success_result_field:

        html_code_after_charge = browser.html

        # チャージられた金額
        result = result_field.value

        account = browser.find_by_id('gc-current-balance').value

        return {
            'code': 1,
            'message': result,
            'html_code_before_charge': html_code_before_charge,
            'html_code_after_charge': html_code_after_charge
        }

    elif gift_charged_message:

        html_code_after_charge = browser.html

        result = browser.find_by_css('div.a-alert-content').value

        return {
            'code': 3,
            'message': result,
            'html_code_before_charge': html_code_before_charge,
            'html_code_after_charge': html_code_after_charge
        }

    elif result_field:
        result = result_field.value

        if result.find(unicode('ギフト券番号は無効です','utf8')) != -1:

            html_code_after_charge = browser.html

            return {
                'code': 3,
                'title': '番号違いエラー',
                'message': '番号違いでエラーが発生しました。',
                'html_code_before_charge': html_code_before_charge,
                'html_code_after_charge': html_code_after_charge
            }

        elif result.find(unicode('セキュリティ検証が無効です', 'utf8')) != -1:

            html_code_after_charge = browser.html

            return {
                'code': 6,
                'message': "チャージするとき画像認証が失敗しました。",
                'html_code_before_charge': html_code_before_charge,
                'html_code_after_charge': html_code_after_charge
            }

        else:

            html_code_after_charge = browser.html

            return get_recent_charge_info(browser, code, html_code_before_charge, html_code_after_charge)

    else:

        html_code_after_charge = browser.html

        return get_recent_charge_info(browser, code, html_code_before_charge, html_code_after_charge)

        # return {
        #     'code': 4,
        #     'title': 'チャージ時エラー',
        #     'message': "Amazonでチャージの手続きを行いましたが、レスポンスが返ってきません。チャージが正常に完了していない可能性があります。",
        #     'html_code_before_charge': html_code_before_charge,
        #     'html_code_after_charge': html_code_after_charge
        # }


def save_history(browser):
    # gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')
    gift_link = browser.find_link_by_href('/gp/gc/ref=nav_cs_gc')
    if gift_link:
        gift_link.click()

        history_link = browser.find_link_by_text(unicode('残高・利用履歴', 'utf8'))

        if history_link:

            history_link.click()

            history = browser.html

            for i in range(0, 3):
                # gift_link = browser.find_link_by_href('/gp/gc/ref=nav_topnav_giftcert')
                gift_link = browser.find_link_by_href('/gp/gc/ref=nav_cs_gc')
                if gift_link:
                    gift_link.click()
                    break
                else:
                    browser.reload()

            charge_link = browser.find_link_by_text(unicode('アカウントに登録', 'utf8'))
            for j in range(0, 3):
                if charge_link:
                    charge_link.click()
                    break
                else:
                    browser.reload()

            return history
        else:
            return None
    else:
        return None


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
    except:

        print 'some problem in captcha'

        return {
            'code': 4,
            'title': 'Amazon接続エラー',
            'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
        }

    # 再ロ入力する
    if code_input_field and captcha_input_field and confirm_button:

        code_input_field.fill(code)
        captcha_input_field.fill(captcha)
        confirm_button.click()

    else:
        return {
            'code': 4,
            'title': 'Amazon接続エラー',
            'message': 'Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。',
        }

    return captcha_get


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
            return {
                'code': 4,
                'title': 'Amazon接続エラー',
                'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
            }

        return captcha_get

    except:

        print 'some problem in captcha'

        return {
            'code': 4,
            'title': 'Amazon接続エラー',
            'message': "Amazonに接続できませんでした。Amazonに問題があるか、AWSとの通信に問題が発生している可能性があります。",
        }


def change_captcha(email):

    browser = BrowserSaver.Browsers().get_browser(email)
    browser.find_by_id('auth-captcha-refresh-link').click()

    time.sleep(1)

    captcha_image_field = browser.find_by_id('auth-captcha-image')

    return captcha_image_field['src']


def get_recent_charge_info(browser, code, html_code_before_charge, html_code_after_charge):
    try:
        browser.find_link_by_href('/gp/gc/ref=nav_cs_gc').click()
        browser.find_link_by_text(unicode('残高・利用履歴', 'utf8')).click()

        table = browser.find_by_css('table.gcYAData')[0]
        trs = table.find_by_tag('tr')
        if len(trs) == 0:
            return {
                'code': 22,
                'title': 'コード入力後エラー',
                'message': "コード入力後、正しくチャージ状態を取得できなっかた。",
                'html_code_before_charge': html_code_before_charge,
                'html_code_after_charge': html_code_after_charge
            }

        recent_charged_code = None
        recent_charged_amount = ""

        for tr in trs:
            tds = tr.find_by_tag('td')
            if not tds:
                continue
            history_type = tds[1].value
            charged_amount = tds[2].value

            if history_type.find(unicode('登録', 'utf8')) != -1:
                recent_charged_code = history_type[-5:-1]
                recent_charged_amount = charged_amount
                break

        if recent_charged_code == code[-4:]:
            return {
                'code': 1,
                'message': recent_charged_amount +'がお客様のギフト券アカウントに追加されました',
                'html_code_before_charge': html_code_before_charge,
                'html_code_after_charge': html_code_after_charge
            }

        else:
            return {
                'code': 22,
                'title': 'コード入力後エラー',
                'message': "コード入力後、正しくチャージ状態を取得できなっかた。",
                'html_code_before_charge': html_code_before_charge,
                'html_code_after_charge': html_code_after_charge
            }

    except:

        return {
            'code': 22,
            'title': 'コード入力後エラー',
            'message': "コード入力後、正しくチャージ状態を取得できなっかた。",
            'html_code_before_charge': html_code_before_charge,
            'html_code_after_charge': html_code_after_charge
        }


def amazon_login_main(email, password, login_captcha):

    # ブラウザを新規する
    # browser = Browser('phantomjs',user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")

    result = []
    # vdisplay = Xvfb()
    # vdisplay.start()

    if login_captcha is False:

        os.environ['DISPLAY'] = ':1'

        browser = Browser('firefox')
        # browser = Browser('phantomjs',
        #                   user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0")
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
            "captcha_src": captcha_image_field['src']
        }

        result = result + [browser]

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

    history = save_history(browser)
    result['html_code_history'] = history

    print code
    # vdisplay.stop()
    return result


if __name__ == '__main__':

    email = ''
    password = ''

    amazon_login_main(email, password, False)