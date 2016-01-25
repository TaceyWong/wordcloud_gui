#coding:utf-8

import os
import json
from Utils import DB,gl

def check():
    try:
        if os.path.exists("config.ini"):
            s = json.load(file("config.ini"))
            DB.DB_HOST = s["DB_IP"]
            DB.DB_DB = s["DB_NAME"]
            DB.DB_USER = s["DB_USER"]
            DB.DB_PWD = s["DB_PWD"]
        if os.path.exists(".ed.ini"):
            return 0
        else:
            gl.DB_CONN, gl.DB_CURSOR = DB.connDB()
            gl.DB_CONN.commit()
            sql1 ="""
                  DROP TABLE IF EXISTS user;
                  CREATE TABLE user (
                  user_name varchar(32) NOT NULL,
                  user_pwd varchar(32) NOT NULL,
                  user_power int(4) DEFAULT NULL,
                  time_created datetime DEFAULT NULL,
                  time_last datetime DEFAULT NULL,
                  PRIMARY KEY (user_name)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
                  INSERT INTO user VALUES (
                                            'admin',
                                            'e10adc3949ba59abbe56e057f20f883e',
                                            '1',
                                            '2016-01-05 23:06:49.000000',
                                            '2016-01-14 18:32:24.000000');
                  INSERT INTO user VALUES (
                                            'user123',
                                            '6ad14ba9986e3615423dfca256d04e3f',
                                            '0',
                                            '2016-01-12 14:07:58.000000',
                                            '2016-01-12 14:07:58.000000');
                """
            sql2 = """
                DROP TABLE IF EXISTS curpos;
                CREATE TABLE curpos (
                lib_name varchar(60) NOT NULL,
                PRIMARY KEY (lib_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                    """
            gl.DB_CURSOR.execute(sql1)
            gl.DB_CONN.commit()
            gl.DB_CURSOR.execute(sql2)
            gl.DB_CONN.commit()


    except Exception,e:
        print e

