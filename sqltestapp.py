# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

#                  dialect+driver://username:password@host:port/database?charset=utf8
# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sc07051989@localhost:3306/userData?charset=utf8'
# 初始化
db = SQLAlchemy(app)

class User(db.Model):
    """ 定义了三个字段， 数据库表名为model名小写
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def save(self):
        db.session.add(self)
        db.session.commit()


# @app.teardown_request
# def shutdown_session(exception=None):
#     db_session.remove()
#
#
# @app.route('/')
# def index():
#     return 'hello world flask'
#
# @app.route('/add/<name>/<email>')
# def add(name, email):
#     u = User(name=name, email=email)
#     try:
#         db_session.add(u)
#         db_session.commit()
#     except Exception, e:
#         return 'wrong'
#     return 'Add %s user successfully' % name
#
# @app.route('/get/<name>')
# def get(name):
#     try:
#         u = User.query.filter(User.name==name).first()
#     except Exception, e:
#         return 'there isnot %s' % name
#     return 'hello %s' % u.name
#
# if __name__ == '__main__':
#     init_db()
#     app.debug = True
#     app.sort = 4001
#     app.run()
