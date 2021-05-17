"""
data base config
author: tj.vincent
date: 2021.4.8
"""
DIALECT = 'mysql'
DRIVER = 'pymysql'
PORT = '3306'
USERNAME = 'root'
# PASSWORD = 'root'
PASSWORD = '123456'
# HOST = '172.17.7.92'
HOST = '172.17.7.93'
# DATABASE = 'case_system_v2'
DATABASE = 'case_system_test'

# mysql 不认识utf-8,而需要直接写成utf8
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
