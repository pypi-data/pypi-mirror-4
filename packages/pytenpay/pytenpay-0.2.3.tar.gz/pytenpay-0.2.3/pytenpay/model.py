#!/usr/bin/env python
#coding:utf-8
import MySQLdb
import DBUtils.PersistentDB

mysql_args= {
    'host': 'localhost',
    'port': 3306, 
    'user': 'root', 
    'passwd': '42qu', 
    'db': 'btc', 
    'charset': 'utf8'
}

persist = DBUtils.PersistentDB.PersistentDB(MySQLdb, 1000, **mysql_args)
connection = persist.connection()

def withdraw_record(user_id, op_time, package_id, pay_amt, bank_no, bank_type, name, desc, phone):
    cur = connection.cursor()
    cur.execute('INSERT INTO Withdraw (user_id, op_time, package_id, pay_amt, bank_no, bank_type, name, `desc`, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (user_id, op_time, package_id, pay_amt, bank_no, bank_type, name, desc, phone))
    return cur._last_executed


if __name__ == "__main__":
    print withdraw_record(1,2,3,4,5,6,'7ss','8sss',9)




