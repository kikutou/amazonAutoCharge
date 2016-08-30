#coding=utf-8
from splinter import Browser
import time

def line_login(browser, user_name, password, code):

    """
    lineに自動ログインして、パラメータのカードコードを入力し、チャージする。
    チャージした結果を返す。

    :param browser:ブラウザインスタンス
    :param user_name:ログインユーザネーム
    :param password:ログインパスワード
    :param code:ギフトカードコード
    :return:チャージ結果
    """
    # ログインページを開く
    browser = Browser('firefox')
    url = 'https://store.line.me/home/'
    browser.visit(url)

    # ログインする
    login_submit = browser.find_link_by_partial_href('login')

    if login_submit:
        login_submit.click()
    else:
        html_code = browser.html
        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }

    username_input_field = browser.find_by_id('id')
    password_input_field = browser.find_by_id('passwd')
    login_submit = browser.find_by_value('Login')

    if username_input_field and password_input_field and login_submit:
        username_input_field.fill(user_name)
        password_input_field.fill(password)
        login_submit.click()
    else:
        html_code = browser.html
        return {
            'code': 4,
            'message': "サイト上に問題が発生しました。（サイトがアクセスできない、またはネットが遅すぎる可能性があります。）",
            'htmlcode': html_code
        }

    # ログイン画像認識があるかどうかチェックする
    #captcha_image_field = browser.find_by_css('img.FnCaptchaImg')

    #メールアドレスまたパスワードをチェックする
    login_alert_field = browser.find_by_css('p.mdMN02Txt')

    if browser.is_element_present_by_css('p.mdMN02Txt'):

        result = login_alert_field.value

        if result.find(unicode('The password you have entered is invalid, or you have not registered your email address with LINE.')) != -1:

            html_code = browser.html

            return {
                'code': 2,
                'message': 'メールアドレスまたはパスワードが正しくありません。',
                'htmlcode': html_code
            }

    # チャージ画面に移動する
    browser.find_by_text('Charge').click()
    browser.windows.current = browser.windows[1]
    browser.find_by_id('70002').click()
    browser.execute_script("charge(this); return false;")

    # チャージする
    code_input_field = browser.find_by_id('FnSerialNumber')

    code_input_field.fill(code)

    time.sleep(9000)

    browser.execute_script("javascript:doCharge(this);return false;")

    result = browser.find_by_css('p.mdLYR11Txt01').value

    browser.quit()

    return result

def line_login_main(user_name, password, code):

    # ブラウザを新規する
    browser = Browser('firefox')

    for x in range(0,3):
        result = line_login(browser, user_name, password, code)

        if result['code'] != 4:
            break

    browser.quit()

    return result

if __name__ == '__main__':

#    data = [
#        {
#            'user_name': 'wangrunbo921',
#            'password': 'wfy04231993',
#            'code': 'hello',
#        },
#        {
#            'user_name': 'juteng2005',
#            'password': 'Juteng378084190',
#            'code': 'good',
#        },
#    ]
#    )


    data = {
        'user_name': '512317052@qq.com',
        'password': 'sc07051989',
        'code': 'hello'
    }

    print line_login_main(data['user_name'],data['password'],data['code'])
