"""
flask api
author: tj.vincent
date: 2021.4.23
"""
from time import time
from sqlalchemy import desc, or_
from configs.exts import *
from flask import jsonify, request, make_response
from sqlalchemy.orm import aliased
from flask_cors import CORS
from configs.auth_list import *
from utils.token_auth import generate_token, get_role_auth, get_info
from utils.trans_time import timestampToTime

CORS(app)  # 实例化跨域对象，解决跨域问题


def make_resp(resp):
    """
    用于添加响应头信息，避免出现跨域问题
    :param resp: 需要返回的响应数据
    :return: 封装后的响应数据
    """
    response = make_response(jsonify(resp))  # 标准json格式转化
    response.headers['content-type'] = 'application:jsoncharset=utf8'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type,x-token'
    return response


@app.route('/user/login', methods=['POST'])
def login():
    """
    传入用户名和密码登录，校验存在用户则生成token
    :param username: 用户名
    :param password: 密码
    :return:
    """
    try:
        sess = Session()
        username = request.json.get('username')
        password = request.json.get('password')
        user_info = sess.query(user).get(username)  # 通过username主键查询是否存在该条数据
        if user_info and user_info.password == password:  # 判断user是否存在，若存在判断密码校验是否一致，否则走下面的流程
            token = generate_token(username, password, user_info.role)  # 生成token
            user_info.update_time = int(time() * 1000)  # 更新user_info的token更新时间
            user_info.token = token  # 更新user_info的token值
            sess.add(user_info)  # 更新user_info对象，新增即为覆盖
            sess.commit()  # 切记使用会话对象需要提交
            sess.close()  # 关闭会话
            res = {"code": 20000, 'data': {"token": token}, "message": "login success"}
        elif user_info:  # 若用户名存在，则提示密码错误
            res = {"code": 40001, "data": {}, "message": "password wrong"}
        else:  # 否则即为未注册用户
            res = {"code": 40002, "data": {}, "message": "user not found"}
    except Exception as e:
        res = {"code": 50000, "data": {}, "message": str(e)}
    resp = make_response(jsonify(res))
    return resp


@app.route('/user/info', methods=['GET'])
def userInfo():
    """
    通过token解析获取用户的数据
    :return:
    """
    token = request.headers.get('X-Token')
    user_info = get_info(token)  # 通过token解析用户信息
    if user_info:
        return make_resp(
            {
                "code": 20000,
                "data": {
                    "roles": [user_info.role],
                    "introduction": f"I am a {user_info.role}",
                    "avatar": user_info.avatar,
                    "name": user_info.name
                },
                "message": "success"
            })
    else:
        return make_resp({"code": 50000, "data": {}, "message": "invalid token"})


@app.route('/user/logout', methods=['GET'])
def logout():
    try:
        sess = Session()
        token = request.headers.get('X-Token')
        user_info = sess.query(user).filter(user.token == token).first()  # 通过token获取到user_info对象
        user_info.update_time = 0  # 将token的时间置空，下次请求会提示token过期
        sess.add(user_info)  # 重写覆盖user_info对象
        sess.commit()  # 提交
        sess.close()  # 关闭会话
        res = {
            'code': 20000,
            'data': {},
            'message': 'log out success'
        }
        sess.close()  # 关闭会话
    except Exception as e:
        res = {
            'code': 50000,
            'data': {},
            'message': str(e)
        }
    return make_resp(res)


@app.route('/business', methods=['GET'])
def getBusiness():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        try:
            sess = Session()
            result = sess.query(business_list).filter(business_list.status == 1).all()
            resp = {'code': 20000, 'data': {'list': [r.business_name for r in result]}, 'message': 'success'}
            sess.close()
        except Exception as e:
            resp = {'code': 50000, 'data': {}, 'message': str(e)}
    response = make_resp(resp)
    return response


@app.route('/module', methods=['GET'])
def getModule():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        try:
            sess = Session()
            business_name = request.args.get('business')
            result = sess.query(module_list).outerjoin(business_list, business_list.business_id == module_list.business_id).filter(
                business_list.business_name == business_name,
                module_list.status == 1
            ).all()
            resp = {'code': 20000, 'data': {'list': [r.module_name for r in result]}, 'message': 'success'}
            sess.close()
        except Exception as e:
            resp = {'code': 50000, 'data': {}, 'message': 'failed'}
    response = make_resp(resp)
    return response


@app.route('/all', methods=['GET'])  # 上线需要下掉该接口
def getAll():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        sess = Session()
        # 获取业务id—name映射表
        business_dict = dict(sess.query(business_list.business_id, business_list.business_name).filter(business_list.status == 1).all())
        # 获取模块id-name映射表
        module_dict = dict(sess.query(module_list.module_id, module_list.module_name).filter(business_list.status == 1).all())
        q = case_list.query
        r = q.paginate(1, q.paginate(1, 1).total)
        result = []  # 定义空列表容器
        for i in r.items:  # 遍历分页对象，得到单个查询对象
            all_attr = i.__dict__  # 获取查询出的对象所有属性、方法
            all_attr.pop('_sa_instance_state')  # 将无效字段移除
            all_attr.pop('status')  # 状态字段仅需要用作过滤条件，无需展示
            b_name = business_dict.get(int(all_attr.pop('business_id')))  # 将查询到的id转为name
            m_name = module_dict.get(int(all_attr.pop('module_id')))  # 将查询到的id转为name
            all_attr['business_name'] = b_name  # 将获取的name写入all_attr
            all_attr['module_name'] = m_name  # 将获取的name写入all_attr
            all_attr['edit_time'] = str(all_attr.get('edit_time'))  # 需要强转为字符串，否则返回格式与数据库不一致
            result.append(all_attr)  # 追加放入列表中
        sess.close()
        resp = {'code': 20000, 'data': {'total': r.total, 'list': result}, 'message': 'success'}
    response = make_resp(resp)
    return response


# 获取table表数据
@app.route('/query', methods=['POST'])
def queryData():
    """
    查询数据
    :return: 查询结果
    """
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        try:
            sess = Session()  # 新建数据库会话对象
            condition = request.json.get('query')  # 获取查询条件
            page = int(request.json.get('page'))  # 获取查询页数
            per_page = int(request.json.get('per_page'))  # 获取单页数据条数
            # 获取查询字段，并去除两端空格判断是否为空（为空则置为空字符串），字段解释详见说明文档
            case_id = condition.get('case_id').strip() if condition.get("case_id") else ''
            case_title = condition.get("case_title").strip() if condition.get("case_title") else ''
            business_name = condition.get('business_name').strip() if condition.get("business_name") else ''
            module_name = condition.get('module_name').strip() if condition.get("module_name") else ''
            editor = condition.get('editor').strip() if condition.get("editor") else ''
            stime = condition.get("edit_stime").strip() if condition.get("edit_stime") else ''
            etime = condition.get("edit_etime").strip() if condition.get("edit_etime") else ''
            # 获取业务id—name映射表
            business_dict = dict(sess.query(business_list.business_id, business_list.business_name).all())
            # 获取模块id-name映射表
            module_dict = dict(sess.query(module_list.module_id, module_list.module_name).all())
            # 不校验业务、模块映射关系均返回（不推荐，易用性较差）
            business_id, module_id = (business_dict.get(business_name), module_dict.get(module_name))
            # print(business_dict, module_dict)
            # 联表查询（校验业务和模块是否关联，后端做补充验证，可注释直接通过传入的名称获取id，参见上方代码）
            # query_result = sess.query(business_list.business_id, module_list.module_id).outerjoin(
            #     business_list, business_list.business_id == module_list.business_id).filter(
            #     or_(business_list.business_name == business_name),
            #     or_(module_list.module_name == module_name, module_name == '')
            # ).first()
            # business_id = query_result[0] if business_name and query_result[0] else ''  # 检查业务名
            # module_id = query_result[1] if module_name and query_result[1] else ''  # 检查模块名
            # 获取查询数据（使用分页对象需要使用table.query语法，会话对象无paginate方法）
            query_data = case_list.query.filter(
                or_(case_list.edit_time >= stime, stime == ''),
                or_(case_list.edit_time <= etime, etime == ''),
                or_(case_list.business_id == business_id, business_id is None),
                or_(case_list.module_id == module_id, module_id is None),
                or_(case_list.case_id == case_id, case_id == ''),
                or_(case_list.case_title == case_title, case_title == ''),
                or_(case_list.editor == editor, editor == ''),
                case_list.status == 1
            ).order_by(
                desc(case_list.edit_time)  # 按照修改时间降序排列
            ).paginate(page, per_page)  # 获取分页对象
            result = []  # 定义空列表容器
            for i in query_data.items:  # 遍历分页对象，得到单个查询对象
                all_attr = i.__dict__  # 获取查询出的对象所有属性、方法
                all_attr.pop('_sa_instance_state')  # 将无效字段移除
                all_attr.pop('case_content')  # 查询页不需要用例详情
                all_attr.pop('status')  # 状态字段仅需要用作过滤条件，无需展示
                b_name = business_dict.get(int(all_attr.pop('business_id')))  # 将查询到的id转为name
                m_name = module_dict.get(int(all_attr.pop('module_id')))  # 将查询到的id转为name
                all_attr['business_name'] = b_name  # 将获取的name写入all_attr
                all_attr['module_name'] = m_name  # 将获取的name写入all_attr
                all_attr['edit_time'] = str(all_attr.get('edit_time'))  # 需要强转为字符串，否则返回格式与数据库不一致
                result.append(all_attr)  # 追加放入列表中
            sess.close()  # 执行完操作后关闭会话对象
            resp = {'code': 20000, 'data': {'total': query_data.total, 'list': result}, 'message': 'success'}
        except Exception as e:
            resp = {'code': 50000, 'data': {}, 'message': str(e)}
    response = make_resp(resp)
    return response


# 查询用例详情
@app.route('/single', methods=['GET'])
def single():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        try:
            sess = Session()  # 新建数据库会话对象
            case_id = request.args.get('case_id')
            res = sess.query(
                case_list.case_title, case_list.editor, case_list.case_content, business_list.business_name, module_list.module_name).outerjoin(
                module_list, module_list.module_id == case_list.module_id).outerjoin(
                business_list, business_list.business_id == case_list.business_id).filter(
                case_list.case_id == case_id
            ).first()
            r = dict(zip(('case_title', 'editor', 'case_content', 'business_name', 'module_name'), res))
            resp = {'code': 20000, 'data': r, 'message': 'success'}
        except Exception as e:
            resp = {'code': 50000, 'data': {}, 'message': str(e)}
        finally:
            sess.close()
    response = make_resp(resp)
    return response


# 添加数据，逐条添加
@app.route('/add', methods=['POST'])
def add_case():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        try:
            sess = Session()
            new_data = request.json
            case_id = new_data.get('case_id')  # 传入id则触发查询修改（若没有查询到则返回异常），不传则为新增
            case_title = new_data.get('case_title')
            business_name = new_data.get('business_name')
            module_name = new_data.get('module_name')
            query_result = sess.query(business_list.business_id, module_list.module_id).outerjoin(business_list, business_list.business_id == module_list.business_id).filter(
                or_(business_list.business_name == business_name),
                or_(module_list.module_name == module_name, module_name == '')
            ).first()
            business_id = query_result[0] if business_name and query_result[0] else ''  # 检查业务名
            module_id = query_result[1] if module_name and query_result[1] else ''  # 检查模块名
            editor = new_data.get('editor')
            edit_time = timestampToTime(time())
            status = new_data.get('status')
            case_content = new_data.get('case_content')
            update_case = sess.query(case_list).get(case_id)
            if update_case:
                update_case.case_title = case_title
                update_case.business_id = business_id
                update_case.module_id = module_id
                update_case.editor = editor
                update_case.edit_time = edit_time
                update_case.status = status
                update_case.case_content = case_content
                sess.commit()
                resp = {'code': 20000, 'data': {'msg': 'case update successfully'}, 'message': 'success'}
            elif case_id:
                resp = {'code': 20000, 'data': {'msg': 'case id not exist'}, 'message': 'failed'}
            else:
                new_case = case_list(case_title, business_id, module_id, editor, edit_time, status, case_content)
                sess.add(new_case)
                sess.commit()
                resp = {'code': 20000, 'data': {'msg': 'case insert successfully'}, 'message': 'success'}
        except Exception as e:
            resp = {'code': 20000, 'data': {'msg': str(e)}, 'message': 'unknown error'}
        finally:
            sess.close()
    response = make_resp(resp)
    return response


# 更新数据，逐条更新
@app.route('/delete', methods=['GET'])
def delete_case():
    try:
        token = request.headers.get('X-Token')  # 获取头信息中的X-Token
        get_role_auth(token, QUERY_LIST)  # 校验权限，第二个位置参数为权限名单
        # pass  # 测试环境无需校验
    except Exception as e:
        resp = {'code': 40003, 'data': [], 'message': str(e)}  # 捕获权限校验抛出的异常（token格式错误或失效）
    else:
        sess = Session()
        case_id = request.args.get('case_id')  # 传入id则触发查询修改（若没有查询到则返回异常），不传则为新增
        del_case = sess.query(case_list).get(case_id)
        del_case.status = 0
        sess.commit()
        resp = {'code': 20000, 'data': {'msg': 'case delete successfully'}, 'message': 'success'}
    response = make_resp(resp)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    # from gevent import pywsgi
    #
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    # server.serve_forever()
