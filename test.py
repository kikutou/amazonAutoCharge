# coding=utf-8
import MySQLdb
import os
secret_key=os.urandom(24)
print secret_key.encode('hex')

# admindb = MySQLdb.connect("localhost", "root", "sc07051989", "admin")
#
# cursor = admindb.cursor()
# u = "vnsuser"
# p = "919vnsuser32"
# ps = "lwkeglw"
#
# sql = 'select * from accounts where account="%s" and password=MD5("%s")' % (u,ps)
#
# cursor.execute(sql)
#
# # 使用 fetchone() 方法获取一条数据库。
# data = cursor.fetchone()
#
# print data
#
# # 关闭数据库连接
# admindb.close()
#
# if data:
#     print 'yes'
# else:
#     print 'no'


