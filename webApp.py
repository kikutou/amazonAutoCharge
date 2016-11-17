# coding=utf-8
# from OpenSSL import SSL
import time
from math import ceil
import demjson
import requests
import os
import zipfile
import random
import MySQLdb
import flask
from flask import Flask, request, render_template, redirect, session, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import BrowserSaver
import amazonBrowser
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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
    gifma_trade_id = db.Column(db.Integer, nullable=True)

    codes = db.relationship('Code', backref='trade')

    def __init__(self, email, serial, gifma_trade_id, start=None, finish=None, status=0):
        self.email = email
        self.serial = serial
        self.gifma_trade_id = gifma_trade_id
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
    :param result:チャージ結果
    :param message:結果のメセージ
    :param balance:チャージ前の残高(html_code)
    :param amount:チャージ後の残高(html_code)
    """

    __tablename__ = 'codes'
    __bind_key__ = 'master'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    gifma_trade_code = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(20), nullable=True)
    result = db.Column(db.Integer)
    message = db.Column(db.Text)
    balance = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Text, nullable=True)
    charge_sum = db.Column(db.Integer, nullable=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))

    def __init__(self, code, gifma_trade_code, time=None, result=None, message=None, balance=None, amount=None, charge_sum=None):
        self.code = code
        self.gifma_trade_code = gifma_trade_code
        self.time = time
        if result is None:
            result = 0
        self.result = result
        self.message = message
        self.balance = balance
        self.amount = amount
        self.charge_sum = charge_sum

    def __repr__(self):
        return '<code: %s>' % (self.code)


@app.route('/', methods=['GET', 'POST'])
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

            sql = 'select * from accounts where account="%s" and password=MD5("%s")' % (u, p)

            cursor.execute(sql)

            user = cursor.fetchone()

            admindb.close()

            if user:
                session['account'] = u

                return redirect('/admin')
            else:
                return render_template('admin-index.html')
        except Exception as e:
            return render_template('admin-index.html')
    else:
        return render_template('admin-index.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


@app.route('/admin', methods=['GET', 'POST'])
def admin(page=1):

    if session and 'account' in session:
        db.create_all()

        list = []

        if 'page' in request.args:
            page = request.args['page']

        if 'search' in request.args:

            session['search_data'] = {
                'search': request.args['search'],
                'word': request.args['word'],
                'ex_s_year': request.args['ex_s_year'],
                'ex_s_month': request.args['ex_s_month'],
                'ex_s_day': request.args['ex_s_day'],
                'ex_e_year': request.args['ex_e_year'],
                'ex_e_month': request.args['ex_e_month'],
                'ex_e_day': request.args['ex_e_day'],
                'ph_s_year': request.args['ph_s_year'],
                'ph_s_month': request.args['ph_s_month'],
                'ph_s_day': request.args['ph_s_day'],
                'ph_e_year': request.args['ph_e_year'],
                'ph_e_month': request.args['ph_e_month'],
                'ph_e_day': request.args['ph_e_day'],
                'status': request.args.getlist('trade_status[]'),
                'order': request.args['order'],
                'limit': request.args['limit']
            }

        if session and 'search_data' in session:

            search = session['search_data']['search']
            word = session['search_data']['word']
            ex_s_year = session['search_data']['ex_s_year']
            ex_s_month = session['search_data']['ex_s_month']
            ex_s_day = session['search_data']['ex_s_day']
            ex_e_year = session['search_data']['ex_e_year']
            ex_e_month = session['search_data']['ex_e_month']
            ex_e_day = session['search_data']['ex_e_day']
            ph_s_year = session['search_data']['ph_s_year']
            ph_s_month = session['search_data']['ph_s_month']
            ph_s_day = session['search_data']['ph_s_day']
            ph_e_year = session['search_data']['ph_e_year']
            ph_e_month = session['search_data']['ph_e_month']
            ph_e_day = session['search_data']['ph_e_day']
            status = session['search_data']['status']
            order = session['search_data']['order']
            limit = session['search_data']['limit']

            trades = Trade.query

            # 検索対象
            if search == 'mail_address' and word:
                trades = trades.filter(Trade.email == word)

            # VNS登録日時
            if ex_s_year and ex_s_month and ex_s_day and ex_e_year and ex_e_month and ex_e_day:
                ex_start_date = ex_s_year+'-'+ex_s_month+'-'+ex_s_day+'00:00:00'
                ex_finish_date = ex_e_year+'-'+ex_e_month+'-'+ex_e_day+'23:59:59'
                trades = trades.filter(Trade.start > ex_start_date, Trade.start < ex_finish_date)

            trades = trades.all()

            trade_ids = []
            for trade in trades:
                trade_ids.append(trade.id)

            codes = Code.query.filter(Code.trade_id.in_(trade_ids))

            # 検索対象
            if search == 'gift_no' and word:
                codes = codes.filter(Code.code == word)
            elif search == 'trade_code' and word:
                codes = codes.filter(Code.gifma_trade_code == word)

            # チェック日時
            if ph_s_year and ph_s_month and ph_s_day and ph_e_year and ph_e_month and ph_e_day:
                ph_start_date = ph_s_year+'-'+ph_s_month+'-'+ph_s_day+'00:00:00'
                ph_finish_date = ph_e_year+'-'+ph_e_month+'-'+ph_e_day+'23:59:59'
                codes = codes.filter(Code.time > ph_start_date, Code.time < ph_finish_date)

            # チェック状況
            if status:
                codes = codes.filter(Code.result.in_(status))

            if order == '3':
                codes = codes.order_by(Code.time.desc())
            elif order == '4':
                codes = codes.order_by(Code.time.asc())

            if limit:
                paginate = codes.paginate(int(page), int(limit), True)
            else:
                paginate = codes.paginate(int(page), 10, True)

            gifcodes_info = paginate.items

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
                    'trade_no': gifcode_info.gifma_trade_code,
                    'charge_sum': gifcode_info.charge_sum,
                    'serial': trade_info.serial
                }

                list.append(info)

            search_data = session['search_data']

        else:
            search_data = None

            paginate = Code.query.order_by(Code.time.desc()).paginate(int(page), 10, True)

            gifcodes_info = paginate.items

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
                    'trade_no': gifcode_info.gifma_trade_code,
                    'charge_sum': gifcode_info.charge_sum,
                    'serial': trade_info.serial
                }

                list.append(info)

        total_page = ceil(paginate.total / paginate.per_page) + 1
        total_page = str(total_page).replace('.0', '')

        count = paginate.total

        return render_template('admin-list.html', list=list, paginate=paginate, total_page=total_page,
                               count=count, session=search_data)
    else:
        return redirect('/')


@app.route('/download')
def download():
    serial = request.args['serial']
    code = request.args['code']

    yyyymmdd = serial[0:8]
    hhmm = serial[8:12]

    url_before = "./trade/"+str(serial)+"/"+code+"/before.html"
    url_after = "./trade/"+str(serial)+"/"+code+"/after.html"
    url_end = "./trade/"+str(serial)+"/"+code+"/history.html"

    url = "./trade/"+str(serial)+"/"+code+"/"+serial+"_"+code+".zip"

    zip_file = zipfile.ZipFile(url, 'w')
    if os.path.exists(url_before):
        zip_file.write(url_before, 'before_'+yyyymmdd+'_'+hhmm+'.html', zipfile.ZIP_DEFLATED)
    if os.path.exists(url_after):
        zip_file.write(url_after, 'after_'+yyyymmdd+'_'+hhmm+'.html', zipfile.ZIP_DEFLATED)
    if os.path.exists(url_end):
        zip_file.write(url_end, 'end_' + yyyymmdd + '_' + hhmm + '.html', zipfile.ZIP_DEFLATED)
    zip_file.close()

    response = make_response(send_file(url))
    response.headers["Content-Disposition"] = "attachment; filename=" + serial+"_"+code+".zip" + ";"
    return response


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

    from_url = request.remote_addr

    email = request.form['email']
    gifma_trade_id = request.form['trade_id']
    email = email.encode("utf-8")
    codes = []
    trade_codes = []

    i = 1

    while('code'+str(i) in request.form):
        codes = codes + [request.form['code'+str(i)]]
        trade_codes = trade_codes + [request.form['trade_code'+str(i)]]
        i += 1

    db.create_all()

    # チャージ開始、ユーザのインフォメーションをダータベースに輸入する
    set_code_for_trade = []
    i = 0
    for code in codes:
        code = code.encode("utf-8")
        code_obj = Code(code=code, gifma_trade_code=trade_codes[i])
        set_code_for_trade = set_code_for_trade + [code_obj]
        i += 1

    serial_time = time.strftime("%Y%m%d%H%M%S")
    serial_no = random.randint(0000, 9999)
    serial = serial_time + str(serial_no)
    while True:
        search_serial = Trade.query.filter_by(serial=serial).all()
        if len(search_serial) == 0:
            break
        serial_no = random.randint(0000, 9999)
        serial = serial_time + str(serial_no)

    trade = Trade(email=email, serial=serial, gifma_trade_id=gifma_trade_id)
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

        j = 0
        for code in codes:

            try:
                charge_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                db.session.query(Code).filter(Code.code == code, Code.trade == trade).update({Code.time: charge_time})

                check_code = Code.query.filter_by(code=code, result='16').all()

                if len(check_code) > 1:

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

                    result = amazonBrowser.amazon_charge_main(browser, code)

                    send_result = ""
                    trade_code = trade_codes[j]
                    charge_sum = 0

                    if result['code'] == 1:
                        # チャージ成功
                        send_result = '16'

                        charge_sum = int(result['message']
                            .replace(unicode('がお客様のギフト券アカウントに追加されました。', 'utf8'), '')
                            .replace(unicode('￥', 'utf8'), '')
                            .replace(unicode(' ', 'utf8'), '')
                            .replace(unicode('　', 'utf8'), '')
                            .replace(unicode(',', 'utf8'), ''))

                    elif result['code'] == 3:
                        # コードは無効
                        send_result = '23'
                    elif result['code'] == 25:
                        # コード未入力エラー
                        send_result = '25'
                    else:
                        # 画像認証失敗まだはページエラー
                        send_result = '22'

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
                        Code.charge_sum: charge_sum
                    })

                    db.session.commit()

                    # Send report to PHP
                    # report = [('code', code), ('result', '1'), ('message', result['message'])]
                    # report = urllib.urlencode(report)
                    # path = 'https://153.121.38.177:9080/amazon_check/db'
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

                response = requests.get("https://"+from_url+"/amazon_check/db", params=report, verify=False)

                response_text = demjson.decode(response.text)

                if response_text['result'] == 'ERROR':
                    trade.status = 3
                    db.session.add(trade)
                    db.session.commit()

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

        # end_history = browser.html
        # file_end_charge = open("./trade/" + str(serial) + "/end.html", "w")
        # file_end_charge.write(str(end_history))
        # file_end_charge.close()

        browser.quit()

        # データベースの削除
        # db.drop_all()

        result = {'result': True}

        return flask.jsonify(result)

        # else:

            # return render_template('buy-checklist.html')

    except:

        # print 'エラーが発生しました'

        db.session.rollback()

        browser = BrowserSaver.Browsers().get_browser(email)

        end_history = browser.html
        file_end_charge = open("./trade/" + str(serial) + "/end.html", "w")
        file_end_charge.write(str(end_history))
        file_end_charge.close()

        browser.quit()

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


if __name__ == '__main__':
    context = ('/etc/apache2/ssl/server.crt', '/etc/apache2/ssl/server.key')
    app.run(debug=True, threaded=True, port=4000, host='0.0.0.0', ssl_context=context)