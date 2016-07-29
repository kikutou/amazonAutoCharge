# coding=utf-8
from flask import Flask, request, render_template, session, redirect
import os
import time
import BrowserSaver
import MySQLdb

import amazonBrowser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# app = Flask(__name__)
app = Flask(__name__, static_url_path='')

#app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


@app.route('/')
def index():
    return render_template('amazon-check.html')


@app.route('/amazon')
def amazon():

    user_name = request.args.get('user_name')
    password = request.args.get('password')

    codes = []

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する
    # start_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
    #
    # db = MySQLdb.connect("localhost", "root", "sc07051989", "webChargeData")
    # cursor = db.cursor()
    #
    # sql = "insert into charge_data(user_email, start_time) values('%s', '%s')" % (user_name, start_time)
    #
    # try:
    #
    #     cursor.execute(sql)
    #     db.commit()
    #
    # except:
    #
    #     db.rollback()

    i = 0
    while True:
        if request.args.get('code' + str(i)):
            codes = codes + [request.args.get('code' + str(i))]
            i += 1
        else:
            break

    captcha = request.args.get('captcha')

    if captcha:
        result = amazonBrowser.amazon_main(user_name, password, codes, captcha)
    else:
        result = amazonBrowser.amazon_main(user_name, password, codes, False)

    # print result

    if len(result) == 2 and result[1]['code'] == 0:

        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(user_name, result[1]['browser'])

        return render_template(
            'index.html',
            captcha=result[0]['htmlcode'],
            user_name=user_name,
            password=password,
            codes=codes
        )

    else:
        return render_template('amazon.html', results=result)


@app.route('/checkStatus', methods=['get'])
def status():

    user_name = request.args.get('user_name')
    password = request.args.get('password')

    fileName = 'charge_status'

    if os.path.exists(fileName):
        txt = open(fileName).read()
    else:
        txt = 'None'

    return txt


@app.route('/changeCaptcha', methods=['get'])
def changeCaptcha():
    user_name = request.args.get('user_name')

    return amazonBrowser.change_captcha(user_name)


# @app.route('/addCode', methods=['get'])
# def addCode():


@app.route('/answer_ajax')
def answer_ajax():
    user_name = request.args.get('user_name')
    password = request.args.get('password')
    codes = request.args.get('code0')

    #search from db

    return 'ok'
    exit;



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4000)
