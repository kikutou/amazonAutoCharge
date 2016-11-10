# coding=utf-8
from flask import Flask, request, render_template, redirect, session, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
import time
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/userData?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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


if __name__ == '__main__':

    ids = []
    trades = db.session.query(Trade).filter(Trade.email == 'juteng2005@gmail.com').all()
    for trade in trades:
        ids.append(trade.id)
        print ids

    result = db.session.query(Code.code, Code.time).filter(Code.trade_id.in_(ids)).all()

    print result