# coding=utf-8
# from OpenSSL import SSL
import time
from math import ceil
import demjson
import requests
import os
import random
import MySQLdb
import flask
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import BrowserSaver
import amazonBrowser
# import sendMail
from splinter import Browser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)

app.secret_key = os.urandom(24).encode('hex')

# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/userData?charset=utf8'
app.config['SQLALCHEMY_BINDS'] = {
    'master': 'mysql://root:123456@localhost:3306/userData?charset=utf8',
    'slave': 'mysql://root:123456@localhost:3306/userData?charset=utf8'
}
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
    __bind_key__ = 'master'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    start = db.Column(db.DateTime, nullable=True)
    finish = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    serial = db.Column(db.CHAR(50), nullable=False, unique=True)

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
    __bind_key__ = 'master'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(20), nullable=True)
    result = db.Column(db.Integer)
    message = db.Column(db.Text)
    balance = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Text, nullable=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))

    def __init__(self, code, time=None, result=None, message=None, balance=None, amount=None):
        self.code = code
        self.time = time
        if result is None:
            result = 0
        self.result = result
        self.message = message
        self.balance = balance
        self.amount = amount

    def __repr__(self):
        return '<code: %s>' % (self.code)


# class Trade(db.Model):
#     """
#     取引先のチャージ情報
#
#     :param email:amazonログインイーメール
#     :param start:チャージが始まる時間
#     :param finish:チャージ終了の時間
#     :param status:取引処理状態(0:未処理, 1:処理中, 2:処理完了, 3:エラー発生)
#     """
#
#     __tablename__ = 'trades_s'
#     __bind_key__ = 'slave'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), nullable=False)
#     start = db.Column(db.DateTime, nullable=True)
#     finish = db.Column(db.DateTime, nullable=True)
#     status = db.Column(db.Integer, nullable=True)
#     serial = db.Column(db.CHAR(50), nullable=False, unique=True)
#
#     codes = db.relationship('Code_s', backref='trade_s')
#
#     def __init__(self, email, serial, start=None, finish=None, status=0):
#         self.email = email
#         self.serial = serial
#         if start is None:
#             start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         self.start = start
#         self.finish = finish
#         self.status = status
#
#     def __repr__(self):
#         return '<user %r traded at %s>' % (self.email, self.start)
#
#
# class Code(db.Model):
#     """
#     チャージするコードの情報
#
#     :param code:ギフト券番号
#     :param sum:ギフト券金額
#     :param result:チャージ結果(0: 確認中, 1: チャージ成功, 2: こーどは無効, 3: エラー発生, 4: ユーザーにメールを送信した)
#     :param message:結果のメセージ
#     :param balance:チャージ前の残高(html_code)
#     :param amount:チャージ後の残高(html_code)
#     """
#
#     __tablename__ = 'codes_s'
#     __bind_key__ = 'slave'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(30), nullable=False)
#     time = db.Column(db.String(20), nullable=True)
#     result = db.Column(db.Integer)
#     message = db.Column(db.Text)
#     balance = db.Column(db.Text, nullable=True)
#     amount = db.Column(db.Text, nullable=True)
#
#     trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))


def __init__(self, code, time=None, result=None, message=None, balance=None, amount=None):
    self.code = code
    self.time = time
    if result is None:
        result = 0
    self.result = result
    self.message = message
    self.balance = balance
    self.amount = amount


def __repr__(self):
    return '<code: %s>' % (self.code)


@app.route('/', methods = ['GET', 'POST'])
def index():
    """
    :return adminログイン画面を表示する。:
    """
    if request.values and request.values['u'] and request.values['p']:
        try:
            u = request.values['u']
            p = request.values['p']

            u = str(u)
            p = str(p)

            admindb = MySQLdb.connect("localhost", "root", "123456", "admin")

            cursor = admindb.cursor()

            sql = 'select * from accounts where account="%s" and password=MD5("%s")' % (u,p)

            cursor.execute(sql)

            user = cursor.fetchone()

            admindb.close()

            if user:
                session['account'] = u

                return redirect('/admin')
            else:
                return render_template('admin-index.html')
        except Exception as e:
            print e
            return render_template('admin-index.html')
    else:
        return render_template('admin-index.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


@app.route('/admin', methods = ['GET', 'POST'])
def admin(page=1):

    if session and session['account']:
        db.create_all()

        list = []

        if 'page' in request.args:
            page = request.args['page']

        if 'search' in request.args:

            try:
                search = request.args['search']
                word = request.args['word']
                ex_s_year = request.args['ex_s_year']
                ex_s_month = request.args['ex_s_month']
                ex_s_day = request.args['ex_s_day']
                ex_e_year = request.args['ex_e_year']
                ex_e_month = request.args['ex_e_month']
                ex_e_day = request.args['ex_e_day']
                ph_s_year = request.args['ph_s_year']
                ph_s_month = request.args['ph_s_month']
                ph_s_day = request.args['ph_s_day']
                ph_e_year = request.args['ph_e_year']
                ph_e_month = request.args['ph_e_month']
                ph_e_day = request.args['ph_e_day']
                status = request.args.getlist('trade_status[]')
                order = request.args['order']
                limit = request.args['limit']

                # print search, word, ex_s_year, ex_s_month, ex_s_day, ex_e_year, ex_e_month, ex_e_day, ph_s_year, \
                #     ph_s_month, ph_s_day, ph_e_year, ph_e_month, ph_e_day, status, order, limit

                if len(status) != 0:
                    status = status + ['', '', '', '']

                # コード関連情報で輪番
                if order == '3' or order == '4':

                    print 'code info'

                    if search == 'gift_no' and word != "":
                        gifcodes_info = Code.query.filter(Code.code == request.args['word'])

                        if len(status) != 0:
                            gifcodes_info = gifcodes_info.filter(
                                or_(Code.result == status[0], Code.result == status[1],
                                    Code.result == status[2], Code.result == status[3],
                                    Code.result == status[4]))

                    else:
                        if len(status) != 0:
                            gifcodes_info = Code.query.filter(
                                or_(Code.result == status[0], Code.result == status[1],
                                    Code.result == status[2], Code.result == status[3],
                                    Code.result == status[4]))
                        else:
                            gifcodes_info = Code.query

                    if order == '3':
                        gifcodes_info = gifcodes_info.order_by(Code.time)
                    else:
                        gifcodes_info = gifcodes_info.order_by(Code.time.desc())

                    if limit == '0':
                        gifcodes_info = gifcodes_info.all()
                    else:
                        gifcodes_info = gifcodes_info.limit(limit).all()

                    for gifcode_info in gifcodes_info:
                        trade_info = gifcode_info.trade

                        if word != '' and ((search == 'mail_address' and trade_info.email != word) or (
                                search == 'trade_code' and trade_info.serial != word)):
                            continue

                        if ex_s_year and ex_e_year and ex_s_month and ex_e_month and ex_s_day and ex_e_day:
                            if str(trade_info.start)[0:4] < ex_s_year or str(trade_info.start)[0:4] > ex_e_year:
                                continue
                            elif ex_s_year == ex_e_year and (
                                    str(trade_info.start)[5:7] < ex_s_month or str(trade_info.start)[
                                                                               5:7] > ex_e_month):
                                continue
                            elif (ex_s_year == ex_e_year and ex_s_month == ex_e_month) and (
                                    str(trade_info.start)[8:10] < ex_s_day or str(trade_info.start)[
                                                                              8:10] > ex_e_day):
                                continue

                        if ph_s_year and ph_e_year and ph_s_month and ph_e_month and ph_s_day and ph_e_day:
                            if str(gifcode_info.time)[0:4] < ph_s_year or str(gifcode_info.time)[
                                                                          0:4] > ph_e_year:
                                continue
                            elif ph_s_year == ph_e_year and (
                                    str(gifcode_info.time)[5:7] < ph_s_month or str(gifcode_info.time)[
                                                                                5:7] > ph_e_month):
                                continue
                            elif (ph_s_year == ph_e_year and ph_s_month == ph_e_month) and (
                                    str(gifcode_info.time)[8:10] < ph_s_day or str(gifcode_info.time)[
                                                                               8:10] > ph_e_day):
                                continue

                        info = {
                            'id': gifcode_info.id,
                            'vns_login_date': str(trade_info.start)[0:10],
                            'vns_login_time': str(trade_info.start)[11::],
                            'charge_start_date': str(gifcode_info.time)[0:10],
                            'charge_start_time': str(gifcode_info.time)[11::],
                            'gift_code': gifcode_info.code,
                            'code_status': gifcode_info.result,
                            'user_email': trade_info.email,
                            'trade_no': trade_info.serial,
                        }

                        list.append(info)

                # 取引関連情報で輪番
                else:

                    if search == 'trade_code' and word != "":
                        trades_info = Trade.query.filter(Trade.serial == word)

                    elif search == 'mail_address' and word != "":
                        trades_info = Trade.query.filter(Trade.email == word)

                    else:
                        trades_info = Trade.query

                    if order == '1':
                        trades_info = trades_info.order_by(Trade.start)
                    else:
                        trades_info = trades_info.order_by(Trade.start.desc())

                    if limit == '0':
                        trades_info = trades_info.all()
                    else:
                        trades_info = trades_info.limit(limit).all()

                    print trades_info

                    for trade_info in trades_info:

                        if ex_s_year and ex_e_year and ex_s_month and ex_e_month and ex_s_day and ex_e_day:
                            if str(trade_info.start)[0:4] < ex_s_year or str(trade_info.start)[0:4] > ex_e_year:
                                continue
                            elif ex_s_year == ex_e_year and (
                                    str(trade_info.start)[5:7] < ex_s_month or str(trade_info.start)[
                                                                               5:7] > ex_e_month):
                                continue
                            elif (ex_s_year == ex_e_year and ex_s_month == ex_e_month) and (
                                    str(trade_info.start)[8:10] < ex_s_day or str(trade_info.start)[
                                                                              8:10] > ex_e_day):
                                continue

                        gifcodes_info = Code.query.filter(Code.trade == trade_info).all()
                        print gifcodes_info

                        for gifcode_info in gifcodes_info:

                            if word != '' and search == 'gift_no' and gifcode_info.code != word:
                                continue

                            if ph_s_year and ph_e_year and ph_s_month and ph_e_month and ph_s_day and ph_e_day:
                                if str(gifcode_info.time)[0:4] < ph_s_year or str(gifcode_info.time)[
                                                                              0:4] > ph_e_year:
                                    continue
                                elif ph_s_year == ph_e_year and (
                                                str(gifcode_info.time)[5:7] < ph_s_month or str(
                                            gifcode_info.time)[5:7] > ph_e_month):
                                    continue
                                elif (ph_s_year == ph_e_year and ph_s_month == ph_e_month) and (
                                                str(gifcode_info.time)[8:10] < ph_s_day or str(
                                            gifcode_info.time)[8:10] > ph_e_day):
                                    continue

                            if len(status) != 0 and str(gifcode_info.result) not in status:
                                continue

                            info = {
                                'id': gifcode_info.id,
                                'vns_login_date': str(trade_info.start)[0:10],
                                'vns_login_time': str(trade_info.start)[11::],
                                'charge_start_date': str(gifcode_info.time)[0:10],
                                'charge_start_time': str(gifcode_info.time)[11::],
                                'gift_code': gifcode_info.code,
                                'code_status': gifcode_info.result,
                                'user_email': trade_info.email,
                                'trade_no': trade_info.serial,
                            }

                            list.append(info)

                return render_template('admin-list.html', list=list, count=len(list))

            except:

                return render_template('admin-list.html')

        else:
            paginate = Code.query.paginate(int(page), 10, True)

            total_page = ceil(paginate.total / paginate.per_page)+1
            total_page = str(total_page).replace('.0', '')

            gifcodes_info = paginate.items

            count = paginate.total
            for gifcode_info in gifcodes_info:
                trade_info = gifcode_info.trade

                info = {
                    'id': gifcode_info.id,
                    'vns_login_date': str(trade_info.start)[0:10],
                    'vns_login_time': str(trade_info.start)[11::],
                    'charge_start_date': str(gifcode_info.time)[0:10],
                    'charge_start_time': str(gifcode_info.time)[11::],
                    'gift_code': gifcode_info.code,
                    'code_status': gifcode_info.result,
                    'user_email': trade_info.email,
                    'trade_no': trade_info.serial,
                }

                list.append(info)

        return render_template('admin-list.html', list=list, paginate=paginate, total_page=total_page,
                               count=count)
    else:
        return redirect('/')


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

    # # 登録成功しない場合は、エラーメセージをメールで送信する。
    # if result['code'] == 4 or result['code'] == 2:
    #     sendMail.sendGmail('wangrunbo921@gmail.com', result['title'], result['message'])

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
    print serial

    trade = Trade(email=email, serial=serial)
    trade.codes = set_code_for_trade

    if not os.path.exists("./trade"):
        os.mkdir("./trade")

    if not os.path.exists("./trade/"+str(serial)):
        os.mkdir("./trade/"+str(serial))

    try:

        db.session.add_all(set_code_for_trade)

        db.session.add(trade)

        db.session.commit()

        browser = BrowserSaver.Browsers().get_browser(email)

        view_charge_page_result = amazonBrowser.view_amazon_charge(browser)

        # 取引状態を処理にします
        trade.status = 1
        db.session.add(trade)
        db.session.commit()

        print codes
        j = 0
        for code in codes:

            try:
                charge_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                check_code = Code.query.filter_by(code=code).all()
                print check_code
                if len(check_code) > 1:

                    print "code exist"

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.time: charge_time,
                        Code.result: '23',
                        Code.message: 'このコードはもう使われました',
                        Code.balance: "",
                        Code.amount: "",
                    })

                    db.session.commit()

                    report = {
                        'code': code,
                        'result': '23',
                        'title': "",
                        'message': 'このコードはもう使われました',
                        'trade_code': trade_codes[j]
                    }
                elif view_charge_page_result is not None:

                    db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({
                        Code.time: charge_time,
                        Code.result: '25',
                        Code.message: 'チャージに移動する時エラーが発生しました。ページ上の問題かもしれません。',
                        Code.balance: "",
                        Code.amount: "",
                    })

                    db.session.commit()

                    report = {
                        'code': code,
                        'result': '25',
                        'title': "",
                        'message': 'チャージに移動する時エラーが発生しました。ページ上の問題かもしれません。',
                        'trade_code': trade_codes[j]
                    }

                else:

                    print code

                    result = amazonBrowser.amazon_charge_main(browser, code)

                    send_result = ""
                    trade_code = trade_codes[j]

                    if result['code'] == 1:
                        # チャージ成功
                        send_result = '16'

                    elif result['code'] == 3:
                        # コードは無効
                        send_result = '23'
                        # sendMail.sendGmail('wangrunbo921@gmail.com', result['title'], result['message'])
                    elif result['code'] == 25:
                        # コード未入力エラー
                        send_result = '25'
                    else:
                        # 画像認証失敗まだはページエラー
                        send_result = '22'
                        # sendMail.sendGmail('wangrunbo921@gmail.com', result['title'], result['message'])

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
                        Code.time: charge_time,
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
                        'title': "",
                        'message': result['message'],
                        'trade_code': trade_code
                    }

                    if 'title' in result:
                        report['title'] = result['title']

                j += 1

                response = requests.get("https://dev01.lifestrage.com/vnc_connect/db", params=report, verify=False)

                print response.status_code

                response_text = demjson.decode(response.text)

                if response_text['result'] == 'ERROR':
                    trade.status = 3
                    db.session.add(trade)
                    db.session.commit()

                    print "response text error"

                    result = {'result': False}

                    return flask.jsonify(result)

            except:

                trade.status = 3
                db.session.add(trade)
                db.session.commit()

                result = {'result': False}

                browser.quit()

                return flask.jsonify(result)

        trade.status = 2
        trade.finish = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(trade)

        db.session.commit()
        browser.quit()

        # データベースの削除
        # db.drop_all()

        result = {'result': True}

        return flask.jsonify(result)

        # else:

            # return render_template('buy-checklist.html')

    except:

        # print 'エラーが発生しました'
        print 'error occur'

        db.session.rollback()

        browser = BrowserSaver.Browsers().get_browser(email)

        browser.quit()

        #db.drop_all()

        # return render_template('buy-checklist.html')
        result = {'result': False}

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


@app.route('/changeCaptcha', methods=['post'])
def changeCaptcha():
    email = request.form['email']
    email = email.encode("utf-8")

    src = amazonBrowser.change_captcha(email)

    result = {'src': src}

    return flask.jsonify(result)


@app.route('/getReq', methods=['get', 'post'])
def getReq():
    if request.form:
        email = request.form['email']
        password = request.form['password']
      
        os.environ['DISPLAY'] = ':1'

        browser = Browser('firefox')
        browser.visit('https://54.238.194.108/')

        return 'post data='+email+'and'+password
    else:
        email = request.args['email']
        password = request.args['password']

        os.environ['DISPLAY'] = ':1'

        browser = Browser('firefox', profile='/tmp/tmphcJ7a7')
        browser.visit('https://54.238.194.108/')

        return 'get data='+email+'and'+password


# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('yourserver.key')
# context.use_certificate_file('yourserver.crt')
if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4000, host='0.0.0.0')
