# coding=utf-8
from flask import Flask, request, render_template, session, redirect
import os
import time
import BrowserSaver
import MySQLdb
from flask_sqlalchemy import SQLAlchemy

import amazonBrowser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# app = Flask(__name__)
app = Flask(__name__, static_url_path='')

# session secret_key
# app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sc07051989@localhost:3306/userData?charset=utf8'
# 初始化
db = SQLAlchemy(app)


class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Unicode(100), nullable=True)
    start = db.Column(db.DateTime, nullable=True)
    finish = db.Column(db.DateTime, nullable=True)

    codes = db.relationship('Code', backref='trade')

    def __init__(self, email, status, start=None, finish=None):
        self.email = email
        self.status = status
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
    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    sum = db.Column(db.Float, nullable=False)
    result = db.Column(db.Text)
    message = db.Column(db.Text)
    balance = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Text, nullable=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))

    def __init__(self, code, sum, result=None, message=None, balance=None, amount=None):
        self.code = code
        self.sum = sum
        if result is None:
            result = 'unused'
        self.result = result
        self.message = message
        self.balance = balance
        self.amount = amount

    def __repr__(self):
        return '<code: %s 金額: %f>' % (self.code, self.sum)


@app.route('/')
def index():
    return render_template('amazon-check.html')


@app.route('/amazon')
def amazon():

    user_name = request.args.get('user_name')
    password = request.args.get('password')

    db.create_all()

    trade = Trade(email=user_name, status='preparing')

    code1 = Code(code='code1111', sum=1000, trade=trade)
    code2 = Code(code='code2222', sum=2000, trade=trade)
    code3 = Code(code='code3333', sum=3000, trade=trade)

    db.session.add_all([trade, code1, code2, code3])

    db.session.commit()

    # codeをデータベースに取得する

    codes = []
    code_obj = Code.query.filter_by(trade=trade).all()

    for code_obj in code_obj:

        code_str = code_obj.code
        codes = codes + [code_str]

    i = 0
    while True:


        # if code_str[i]:
        #     codes = codes + [code_str[i].code]
        #     i += 1
        # else:
        #     break

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する



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
