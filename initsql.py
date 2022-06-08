# -*- coding = utf-8 -*-
# @Time : 2022/6/6 19:33
# @Author : SBP
# @File : initaql.py
# @Software : PyCharm

import sqlite3

path = './datas/logins/db.sqlite3'
conn = sqlite3.connect(path)
cur = conn.cursor()
sql = 'create table Persons (id INTEGER primary key autoincrement, name VARCHAR(20) not null ,picpath VARCHAR(128) not null, respath VARCHAR(128),optime VARCHAR(16))'
cur.execute(sql)
cur.close()
conn.close()
