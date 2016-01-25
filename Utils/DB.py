#coding:utf-8
import MySQLdb

DB_HOST = "localhost"
DB_PORT = "3306"
DB_USER = "root"
DB_PWD = ""
DB_DB = "wxapp"
DB_CHARTSET = "utf8"
def connDB():
    try:
        conn=MySQLdb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_DB,charset=DB_CHARTSET)
        cursor = conn.cursor()
    except:
        pass
    return conn,cursor

def closeDB(conn):
    try:
        conn.close
    except:
        pass
