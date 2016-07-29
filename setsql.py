# -*- coding: utf-8 -*-

from sqltestapp import db, User

u = User(username='admin', email='admin@example.com')
db.session.add(u)                                     # 添加session
db.session.commit()                                   # 提交查询
users = User.query.all()                              # 查询

# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
#
# engine = create_engine('mysql:///./test.db', convert_unicode=True) # 创建数据库引擎( 当前目录下保存数据库文件)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
# Base = declarative_base()
# Base.query = db_session.query_property()
#
# def init_db():
#     # 在这里导入所有的可能与定义模型有关的模块，这样他们才会合适地
#     # 在 metadata 中注册。否则，您将不得不在第一次执行 init_db() 时
#     # 先导入他们。
#     import models
#     Base.metadata.create_all(bind=engine)


