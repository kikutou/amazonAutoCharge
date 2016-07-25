#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

db = MySQLdb.connect("localhost", "root", "123456", "DBTEST")

db.close()