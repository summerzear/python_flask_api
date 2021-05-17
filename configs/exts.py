"""
数据库表结构
author: tj.vincent
date: 2021.4.25
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from configs import config
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config.from_object(config)
DB = SQLAlchemy(app)  # 实例化数据库对象，用于建表
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)  # 新建数据库引擎
Session = sessionmaker(bind=engine)  # 新建数据库会话类


class user(DB.Model):
    """
    用户表
    """
    username = DB.Column(DB.VARCHAR(50), nullable=False, primary_key=True)  # 用户名
    name = DB.Column(DB.VARCHAR(50), nullable=False)  # 姓名
    password = DB.Column(DB.VARCHAR(50), nullable=False)  # 密码
    role = DB.Column(DB.VARCHAR(50), nullable=False)  # 角色
    token = DB.Column(DB.VARCHAR(255))  # token值
    update_time = DB.Column(DB.VARCHAR(50))  # token更新时间
    avatar = DB.Column(DB.VARCHAR(255))  # 头像

    def __init__(self, name, username, password, update_time, role='user', token=None, avatar=None):
        self.name = name
        self.username = username
        self.password = password
        self.role = role
        self.avatar = avatar
        self.token = token
        self.update_time = update_time


class case_list(DB.Model):
    """
    用例表结构
    """
    case_id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)  # 用例id，自增主键
    case_title = DB.Column(DB.VARCHAR(50), nullable=False)  # 用例标题
    business_id = DB.Column(DB.INT, nullable=False)  # 业务id（详见业务表）
    module_id = DB.Column(DB.INT, nullable=False)  # 模块id（详见模块表）
    editor = DB.Column(DB.VARCHAR(50), nullable=False)  # 编辑者
    edit_time = DB.Column(DB.DATETIME, nullable=False)  # 最后编辑时间
    status = DB.Column(DB.INT, nullable=False)  # 状态（0删除，1正常）
    case_content = DB.Column(DB.TEXT)

    def __init__(self, case_title, business_id, module_id, editor, edit_time, status, case_content):
        self.case_id = None  # 自增主键，无需传入
        self.case_title = case_title
        self.business_id = business_id
        self.module_id = module_id
        self.editor = editor
        self.edit_time = edit_time
        self.status = status
        self.case_content = case_content


class business_list(DB.Model):
    """
    业务表结构
    """
    business_id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)  # 业务id，自增主键
    business_name = DB.Column(DB.VARCHAR(255), nullable=False, unique=True)  # 业务名，唯一键
    status = DB.Column(DB.INT, nullable=False)  # 状态（0删除，1正常）

    def __init__(self, business_name, status):
        self.business_id = None
        self.business_name = business_name
        self.status = status


class module_list(DB.Model):
    """
    模块表结构
    """
    module_id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)  # 模块id，自增主键
    module_name = DB.Column(DB.VARCHAR(255), nullable=False)  # 模块名
    business_id = DB.Column(DB.INT, nullable=False)  # 关联业务id
    status = DB.Column(DB.INT, nullable=False)  # 状态（0删除，1正常）

    def __init__(self, module_name, status, business_id):
        self.module_id = None
        self.module_name = module_name
        self.status = status
        self.business_id = business_id


# 下方的数据库建表暂时不执行
# class bug_list(DB.Model):
#     """
#     bug_list表结构
#     """
#     bugid = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)
#     bugcontent = DB.Column(DB.VARCHAR(255), nullable=False)
#     testuser = DB.Column(DB.VARCHAR(255))
#     caselist = DB.Column(DB.VARCHAR(255))
#     status = DB.Column(DB.VARCHAR(255))
#     businesskey = DB.Column(DB.VARCHAR(255))
#     functionalkey = DB.Column(DB.VARCHAR(255))
#
#     def __init__(self, bugcontent, testuser, caselist, status, businesskey, functionalkey):
#         self.bugid = None
#         self.testuser = testuser
#         self.bugcontent = bugcontent
#         self.caselist = caselist
#         self.status = status
#         self.businesskey = businesskey
#         self.functionalkey = functionalkey
# class tasklist(DB.Model):
#     """
#     tasklist表结构
#     """
#     id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)
#     caseid = DB.Column(DB.VARCHAR(255))
#     status = DB.Column(DB.INT)
#     content = DB.Column(DB.VARCHAR(255))
#     create_time = DB.Column(DB.VARCHAR(10))
#     creator = DB.Column(DB.VARCHAR(20))
#     tasklist_id = DB.Column(DB.INT)
#     remark = DB.Column(DB.VARCHAR(255))
#     taskname = DB.Column(DB.VARCHAR(255))
#
#     def __init__(self, caseid, status, content, create_time, creator, tasklist_id, remark, taskname):
#         self.id = None
#         self.caseid = caseid
#         self.status = status
#         self.content = content
#         self.create_time = create_time
#         self.creator = creator
#         self.tasklist_id = tasklist_id
#         self.remark = remark
#         self.taskname = taskname


# class tasklist_content(DB.Model):
#     """
#     tasklist_content表结构
#     """
#     id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)
#     tasklist_id = DB.Column(DB.INT)
#     caseid = DB.Column(DB.VARCHAR(255))
#     creator = DB.Column(DB.VARCHAR(40))
#     case_content = DB.Column(DB.VARCHAR(255))
#     create_time = DB.Column(DB.VARCHAR(20))
#     update_time = DB.Column(DB.VARCHAR(20))
#     status = DB.Column(DB.INT)
#     remark = DB.Column(DB.VARCHAR(255))
#     result = DB.Column(DB.INT)
#     task_round = DB.Column(DB.INT)
#
#     def __init__(self, tasklist_id, caseid, creator, case_content, create_time, update_time, status, remark, result, task_round):
#         self.id = None
#         self.tasklist_id = tasklist_id
#         self.caseid = caseid
#         self.creator = creator
#         self.case_content = case_content
#         self.create_time = create_time
#         self.update_time = update_time
#         self.status = status
#         self.remark = remark
#         self.result = result
#         self.task_round = task_round


# class time_count(DB.Model):
#     """
#     time_count表结构
#     """
#     id = DB.Column(DB.INT, primary_key=True, autoincrement=True, nullable=False)
#     tasklist_id = DB.Column(DB.INT)
#     starttime = DB.Column(DB.VARCHAR(255))
#     endtime = DB.Column(DB.VARCHAR(255))
#     status = DB.Column(DB.VARCHAR(255))
#     type = DB.Column(DB.INT)
#     task_round = DB.Column(DB.INT)
#
#     def __init__(self, tasklist_id, starttime, endtime, status, type, task_round):
#         self.id = None
#         self.tasklist_id = tasklist_id
#         self.starttime = starttime
#         self.endtime = endtime
#         self.status = status
#         self.type = type
#         self.task_round = task_round


if __name__ == '__main__':
    # DB.drop_all()  # 删所有库
    # DB.create_all()  # 建所有库
    pass
