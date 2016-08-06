# coding=utf-8
import flask
from flask import Flask, request, render_template, session, redirect
import os
import time
import BrowserSaver
import MySQLdb
from flask_sqlalchemy import SQLAlchemy
import demjson

import amazonBrowser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# app = Flask(__name__)
app = Flask(__name__, static_url_path='')

# # session secret_key
# # app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sc07051989@localhost:3306/userData?charset=utf8'
# 初始化
db = SQLAlchemy(app)


# class User(db.Model):
#     __tablename__ = 'User'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.VARCHAR(10), nullable=False)
#     sum = db.Column(db.Integer, nullable=False)
#
#     def __init__(self, code, sum):
#         self.code = code
#         self.sum = sum
#
#     def __repr__(self):
#         return '<code: %s 金額: %f>' % (self.code, self.sum)
#
#
class Trade(db.Model):
    """
    取引先のチャージ情報

    :param email:amazonログインイーメール
    :param start:チャージが始まる時間
    :param finish:チャージ終了の時間
    """

    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    start = db.Column(db.DateTime, nullable=True)
    finish = db.Column(db.DateTime, nullable=True)

    codes = db.relationship('Code', backref='trade')

    def __init__(self, email, start=None, finish=None):
        self.email = email
        if start is None:
            start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.start = start
        self.finish = finish

    def __repr__(self):
        return '<user %r traded at %s>' % (self.email, self.start)

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()


class Code(db.Model):
    """
    チャージするコードの情報

    :param code:ギフト券番号
    :param sum:ギフト券金額
    :param result:チャージ結果(0: 確認中, 1: チャージ成功, 2: こーどは無効, 3: エラー発生, 4: ユーザーにメールを送信した)
    :param message:結果のメセージ
    :param balance:チャージ前の残高(htmlcode)
    :param amount:チャージ後の残高(htmlcode)
    """

    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    sum = db.Column(db.Float, nullable=False)
    result = db.Column(db.Integer)
    message = db.Column(db.Text)
    balance = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Text, nullable=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))

    def __init__(self, code, sum, result=None, message=None, balance=None, amount=None):
        self.code = code
        self.sum = sum
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
    return render_template('amazon-check.html')


@app.route('/amazon-login', methods=['post'])
def amazon_login():

    print request.form['email']

    email = request.form['email']
    password = request.form['password']

    captcha = request.args.get('captcha')

    #email = demjson.decode(email_json)
    #password = demjson.decode(password_json)

    if captcha:
        data = amazonBrowser.amazon_login_main(email, password, captcha)
    else:
        data = amazonBrowser.amazon_login_main(email, password, False)

    # 登録成功
    if data[0]['code'] == 7:
        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(email, data[1])



        # codes = []
        #
        # all_code = User.query.all()
        # for code in all_code:
        #     codes = codes + [code]
        #
        # return render_template('buy-checklist.html',
        #                        email=email,
        #                        codes=codes)

    # 認証画面がある場合
    # elif len(result) == 2 and result[1]['code'] == 0:
    #
    #     browser_list = BrowserSaver.Browsers()
    #     browser_list.set_browser(email, result[1]['browser'])

        # return render_template(
        #     'amazon-check-img.html',
        #     captcha=result[0]['htmlcode'],
        #     email=email,
        #     password=password
        # )

    # # 登録失敗の場合
    # elif result[0]['code'] == 2:
    #     print '登録失敗'
    #     return render_template(
    #         'amazon-error.html',
    #         email=email,
    #         password=password
    #     )
    #
    # else:
    #     print 'Error'
    #     return render_template('amazon-check.html')

    #result = demjson.encode([data[0]])
    result = data[0]

    print result

    return flask.jsonify(result)


@app.route('/buy-checklist', methods=['post'])
def auto_charge():

    email = request.form['email']
    codes = request.form['codes']

    print 'charge_codes' + '---' + email

    # email = demjson.decode(email_json)
    # codes = demjson.decode(codes_json)

    db.create_all()

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する

    # get_code_from_user = User.query.all()
    set_code_for_trade = []
    for user_code_data in codes:
        code_obj = Code(code=user_code_data.code, sum=user_code_data.par_amount)
        set_code_for_trade = set_code_for_trade + [code_obj]

    trade = Trade(email=email)
    # trade.codes = [code1, code2, code3, code4]
    trade.codes = set_code_for_trade

    try:
        # db.session.add_all([code1, code2, code3, code4])
        db.session.add_all(set_code_for_trade)

        db.session.commit()

        db.session.add(trade)

        # codeをデータベースに取得する

        codes = []

        code_all = db.session.query(Code).filter(Code.trade == trade).all()

        # code_all = Code.query.filter_by(trade=trade).all()

        for code_data in code_all:
            code_str = code_data.code
            codes = codes + [code_str]

        if email:

            browser = BrowserSaver.Browsers().get_browser(email)

            amazonBrowser.view_amazon_charge(browser)

            for code in codes:

                result = amazonBrowser.amazon_charge_main(browser, code)

                if result['code'] == 1:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 1,
                        Code.message: result['message'],
                        Code.balance: result['htmlcode'],
                        Code.amount: result['htmlcode']
                    })
                    db.session.commit()

                elif result['code'] == 3:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 2,
                        Code.message: result['message'],
                        Code.balance: result['htmlcode']
                    })
                    db.session.commit()

                else:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 3,
                        Code.message: result['message'],
                        Code.balance: result['htmlcode']
                    })
                    db.session.commit()

            trade.finish = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            db.session.commit()
            browser.quit()

            # return render_template('buy-list.html')
        result = {'result': True}

        #demjson.encode(result)
        return flask.jsonify(result)

        # else:

            # return render_template('buy-checklist.html')


    except:

        print 'エラーが発生しました'

        db.session.rollback()

        # return render_template('buy-checklist.html')
        result = {'result': False}

        #demjson.encode(result)
        return flask.jsonify(result)


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


@app.route('/changeCaptcha', methods=['get'])
def changeCaptcha():
    email = request.args.get('email')

    return amazonBrowser.change_captcha(email)


# @app.route('/addCode', methods=['get'])
# def addCode():


# @app.route('/answer_ajax')
# def answer_ajax():
#     email = request.args.get('email')
#     password = request.args.get('password')
#     codes = request.args.get('code0')
#
#     #search from db
#
#     return 'ok'
#     exit;


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4000, host='0.0.0.0')
