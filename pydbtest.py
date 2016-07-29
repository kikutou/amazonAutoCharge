#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import time

now = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime())
print now

db = MySQLdb.connect("localhost", "root", "sc07051989", "test")

cursor = db.cursor()

sql = "insert into test(name, class, grade, time) values('li', '3', 1, '%s')" % (now)

cursor.execute(sql)

db.commit()

sql = 'select * from test'

cursor.execute(sql)

result = cursor.fetchall()
print result

db.close()

