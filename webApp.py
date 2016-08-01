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
    :param result:チャージ結果(checking: 確認中, success: チャージ成功, unavailable: こーどは無効, error: エラー発生, sent: ユーザーにメールを送信した)
    :param message:結果のメセージ
    :param balance:チャージ前の残高(htmlcode)
    :param amount:チャージ後の残高(htmlcode)
    """

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
            result = 'checking'
        self.result = result
        self.message = message
        self.balance = balance
        self.amount = amount

    def __repr__(self):
        return '<code: %s 金額: %f>' % (self.code, self.sum)


@app.route('/')
def index():
    return render_template('amazon-check.html')


@app.route('/amazon-login')
def amazon_login():

    email = request.args.get('email')
    password = request.args.get('password')

    captcha = request.args.get('captcha')

    if captcha:
        result = amazonBrowser.amazon_login_main(email, password, captcha)
    else:
        result = amazonBrowser.amazon_login_main(email, password, False)

    # print result

    # 登録成功
    if result[0]['code'] == 7:
        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(email, result[1])
        print email
        return render_template('buy-checklist.html', email=email)

    # 認証画面がある場合
    elif len(result) == 2 and result[1]['code'] == 0:

        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(email, result[1]['browser'])

        return render_template(
            'amazon-check-img.html',
            captcha=result[0]['htmlcode'],
            email=email,
            password=password
        )

    # 登録失敗の場合
    elif result[0]['code'] == 2:
        return render_template(
            'amazon-error.html',
            email=email,
            password=password
        )

    else:
        print 'Error'
        return render_template('amazon-check.html')


@app.route('/buy-checklist', methods=['get'])
def auto_charge():

    email = request.args.get('email')
    print email

    db.create_all()

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する

    trade = Trade(email=email)

    code1 = Code(code='code1111', sum=1000)
    code2 = Code(code='code2222', sum=2000)
    code3 = Code(code='code3333', sum=3000)

    trade.codes = [code1, code2, code3]

    try:
        db.session.add_all([trade, code1, code2, code3])

        # codeをデータベースに取得する

        codes = []
        print 'charge start run'
        code_all = db.session.query(Code).filter(Code.trade == trade).all()
        print "code_all"
        print code_all
        # code_all = Code.query.filter_by(trade=trade).all()

        for code_data in code_all:
            code_str = code_data.code
            codes = codes + [code_str]

        if email:
            print 'email exist'
            browser = BrowserSaver.Browsers().get_browser(email)
            print 'browser'
            print browser

            for code in codes:
                result = amazonBrowser.amazon_charge_main(browser, code)

                if result['code'] == 1:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 'success',
                        Code.message: result['message'],
                        Code.balance: result['htmlcode'],
                        Code.amount: result['htmlcode']
                    })

                elif result['code'] == 3:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 'unavailable',
                        Code.message: result['message'],
                        Code.balance: result['htmlcode']
                    })

                else:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.result: 'error',
                        Code.message: result['message'],
                        Code.balance: result['htmlcode']
                    })

            trade.finish = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            db.session.commit()

            return render_template('buy-list.html')

        else:
            return render_template('buy-checklist.html')

    except:

        print 'エラーが発生しました'

        db.session.rollback()

        return render_template('buy-checklist.html')



@app.route('/checkStatus', methods=['get'])
def status():

    email = request.args.get('email')
    password = request.args.get('password')

    fileName = 'charge_status'

    if os.path.exists(fileName):
        txt = open(fileName).read()
    else:
        txt = 'None'

    return txt


@app.route('/changeCaptcha', methods=['get'])
def changeCaptcha():
    email = request.args.get('email')

    return amazonBrowser.change_captcha(email)


# @app.route('/addCode', methods=['get'])
# def addCode():


@app.route('/answer_ajax')
def answer_ajax():
    email = request.args.get('email')
    password = request.args.get('password')
    codes = request.args.get('code0')

    #search from db

    return 'ok'
    exit;



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4080)
