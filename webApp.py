# coding=utf-8
import time
import demjson
import requests
import os
import random
import flask
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import BrowserSaver
import amazonBrowser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__, static_url_path='')

# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/userData?charset=utf8'
# 初始化
db = SQLAlchemy(app)


class Trade(db.Model):
    """
    取引先のチャージ情報

    :param email:amazonログインイーメール
    :param start:チャージが始まる時間
    :param finish:チャージ終了の時間
    :param status:取引処理状態(0:未処理, 1:処理中, 2:処理完了, 3:エラー発生)
    """

    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    start = db.Column(db.DateTime, nullable=True)
    finish = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    serial = db.Column(db.CHAR(10), nullable=False, unique=True)

    codes = db.relationship('Code', backref='trade')

    def __init__(self, email, serial, start=None, finish=None, status=0):
        self.email = email
        self.serial = serial
        if start is None:
            start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.start = start
        self.finish = finish
        self.status = status

    def __repr__(self):
        return '<user %r traded at %s>' % (self.email, self.start)


class Code(db.Model):
    """
    チャージするコードの情報

    :param code:ギフト券番号
    :param sum:ギフト券金額
    :param result:チャージ結果(0: 確認中, 1: チャージ成功, 2: こーどは無効, 3: エラー発生, 4: ユーザーにメールを送信した)
    :param message:結果のメセージ
    :param balance:チャージ前の残高(html_code)
    :param amount:チャージ後の残高(html_code)
    """

    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    result = db.Column(db.Integer)
    message = db.Column(db.Text)
    balance = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Text, nullable=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))

    def __init__(self, code, result=None, message=None, balance=None, amount=None):
        self.code = code
        if result is None:
            result = 0
        self.result = result
        self.message = message
        self.balance = balance
        self.amount = amount

    def __repr__(self):
        return '<code: %s 金額: %f>' % (self.code, self.sum)


@app.route('/')
def index():
    """
    テスト用
    :return テスト画面を表示する。:
    """
    return render_template('amazon-check.html')


@app.route('/amazon-login', methods=['post'])
def amazon_login():
    """
    amazonにログインする。
    状況として、
    ①ログインのメールアドレスとパスワードだけ
    ②ログインのメールアドレス、パスワードと画像認証
    :return　ログインの結果を返す:
    """
    print request.form['email'] + "のログインを開始する。"

    email = request.form['email']
    password = request.form['password']

    if 'captcha' in request.form.keys():

        captcha = request.form['captcha']

        data = amazonBrowser.amazon_login_main(email, password, captcha)
    else:

        data = amazonBrowser.amazon_login_main(email, password, False)

    # 登録成功 or 認証画面
    if data[0]['code'] == 7 or data[0]['code'] == 8:
        # 登録成功の場合、このブラウザオブジェクトをゴロバルリストに保存する。
        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(email, data[1])

    result = data[0]

    return flask.jsonify(result)


@app.route('/buy-checklist', methods=['post'])
def auto_charge():

    email = request.form['email']
    email = email.encode("utf-8")
    codes = []
    trade_codes = []

    i = 1

    while('code'+str(i) in request.form):
        codes = codes + [request.form['code'+str(i)]]
        trade_codes = trade_codes + [request.form['trade_code'+str(i)]]
        i += 1

    print "取得されたコードは："
    print codes

    db.create_all()

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する
    set_code_for_trade = []
    for code in codes:
        code = code.encode("utf-8")
        code_obj = Code(code=code)
        set_code_for_trade = set_code_for_trade + [code_obj]

    serial_time = time.strftime("%Y%m%d%H%M%S")
    serial_no = random.randint(0000, 9999)
    serial = serial_time + str(serial_no)
    while True:
        search_serial = Trade.query.filter_by(serial=serial).all()
        if len(search_serial) == 0:
            break
        serial_no = random.randint(0000, 9999)
        serial = serial_time + str(serial_no)

    trade = Trade(email=email, serial=serial)
    trade.codes = set_code_for_trade

    if not os.path.exists("./trade"):
        os.mkdir("./trade")

    if not os.path.exists("./trade/"+str(serial)):
        os.mkdir("./trade/"+str(serial))

    #try:

    db.session.add_all(set_code_for_trade)

    db.session.add(trade)

    db.session.commit()

    browser = BrowserSaver.Browsers().get_browser(email)

    amazonBrowser.view_amazon_charge(browser)

    # 取引状態を処理にします
    trade.status = 1
    db.session.add(trade)
    db.session.commit()

    j = 0
    for code in codes:

        #try:

        result = amazonBrowser.amazon_charge_main(browser, code)

        send_result = ""
        trade_code = trade_codes[j]

        if result['code'] == 1:
            # チャージ成功
            send_result = '16'

        elif result['code'] == 3:
            # コードは無効
            send_result = '23'

        else:
            # 画像認証失敗まだはページエラー
            send_result = '22'

        print send_result

        if not os.path.exists("./trade/"+str(serial)+"/"+code):
            os.mkdir("./trade/"+str(serial)+"/"+code)

        file_before_charge = open("./trade/"+str(serial)+"/"+code+"/before.html", "w")
        file_before_charge.write(str(result['html_code_before_charge']))
        file_before_charge.close()

        file_after_charge = open("./trade/"+str(serial)+"/"+code+"/after.html", "w")
        file_after_charge.write(str(result['html_code_after_charge']))
        file_after_charge.close()

        file_history = open("./trade/"+str(serial)+"/"+code+"/history.html", "w")
        file_history.write(str(result['html_code_history']))
        file_history.close()

        db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
            Code.result: send_result,
            Code.message: result['message'],
            Code.balance: "./trade/"+str(serial)+"/"+code+"/before.html",
            Code.amount: "./trade/"+str(serial)+"/"+code+"/after.html",
        })

        db.session.commit()

        # Send report to PHP
        # report = [('code', code), ('result', '1'), ('message', result['message'])]
        # report = urllib.urlencode(report)
        # path = 'https://153.121.38.177:9080/vnc_connect/db'
        # req = urllib2.Request(path, report)
        # req.add_header("Content-type", "application/x-www-form-urlencoded")
        # page = urllib2.urlopen(req).read()
        # print page

        report = {
            'code': code,
            'result': send_result,
            'message': result['message'],
            'trade_code': trade_code
        }

        j += 1

        print 'send report'
        response = requests.get("https://dev01.lifestrage.com/vnc_connect/db", params=report, verify=False)

        print response.status_code

        print 'req'
        print response.text

        response_text = demjson.decode(response.text)

        print type(response_text)

        print response_text['result']
        print response
        print response.content
        # print response.content['result']

        if response_text['result'] == 'ERROR':
            trade.status = 3
            db.session.add(trade)
            db.session.commit()

            print "response text error"

            result = {'result': False}

            return flask.jsonify(result)

        # except:
        #
        #     print "db update fail"
        #
        #     trade.status = 3
        #     db.session.add(trade)
        #     db.session.commit()
        #
        #     result = {'result': False}
        #
        #     browser.quit()
        #
        #     return flask.jsonify(result)

    trade.status = 2
    trade.finish = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db.session.add(trade)

    db.session.commit()
    browser.quit()

    # データベースの削除
    #db.drop_all()

    result = {'result': True}

    return flask.jsonify(result)

    # else:

        # return render_template('buy-checklist.html')

    # except:
    #
    #     # print 'エラーが発生しました'
    #     print 'error occur'
    #
    #     db.session.rollback()
    #
    #     browser = BrowserSaver.Browsers().get_browser(email)
    #
    #     browser.quit()
    #
    #     #db.drop_all()
    #
    #     # return render_template('buy-checklist.html')
    #     result = {'result': False}
    #
    #     return flask.jsonify(result)


@app.route('/checkStatus', methods=['get'])
def status():

    db.create_all()

    email = request.args.get('email')
    code = request.args.get('code')

    charge_status = 0

    while True:
        time.sleep(3)
        code_info = Code.query.filter_by(code=code).first()
        charge_status = code_info.result

        if charge_status != 0:
            break

    if charge_status == 1:
        return 'success'
    elif charge_status == 2:
        return 'unavailable'
    else:
        return 'error'


@app.route('/changeCaptcha', methods=['post'])
def changeCaptcha():
    email = request.form['email']
    email = email.encode("utf-8")

    src = amazonBrowser.change_captcha(email)

    result = {'src': src}

    return flask.jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4000, host='0.0.0.0')
