import base64
from json import dumps, loads
from time import time
from configs.exts import user

TOKEN_DURATION = 3 * 24 * 60 * 60 * 1000 # 定义token时效，单位毫秒


def get_info(token):
    """
    token反查数据库user数据
    :param token:
    :return:
    """
    data = user.query.filter(user.token == token).first()
    return data


def generate_token(username, password, role):
    """
    登录生成token
    :param username: 用户名
    :param password: 密码
    :param role: 角色
    :return:
    """
    source = {
        "username": username,
        "role": role,
        "password": password[:-4:-1] + password[:3],  # 密码乱序（PS：密码最少6位，按位置索引：-1，-2，-3，1，2，3）
        "timestamp": int(time() * 1000)
    }
    token = (base64.b64encode((dumps(source)).encode('utf-8'))).decode('utf-8')  # base64加密
    return token


def get_role_auth(token: str, auth_role):
    """
    传入token，解码获取角色，用于校验接口权限
    :param token: 传入token值，指定字符串类型
    :return: token解析出的角色
    """
    try:
        user_info = get_info(token)
        role = user_info.role
        timestamp = int(user_info.update_time)
    except:
        raise Exception('token is invalid')  # 若解码数据有误，则抛出token无效的异常
    else:
        if role in auth_role:  # 判断用户是否在名单中
            if int(time() * 1000) - timestamp < TOKEN_DURATION:  # 判断token是否过期
                return True
            else:
                raise Exception('token is out of date')  # token过期
        else:
            raise Exception('no authorization')  # 无权限


if __name__ == '__main__':
    # source = {'asdf':"123453","124":'21fsdaf','fdge':'dfga1'}
    # print(base64.b64encode(dumps(source).encode('utf-8')).decode('utf-8'))
    # t = generate_token('admin', '1234567890', 'admin')
    # print(t)
    # print(get_role_auth(t, ['admin']))
    print(get_role_auth('eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJyb2xlIjogImFkbWluIiwgInBhc3N3b3JkIjogIjMyMWFkbSIsICJ0aW1lc3RhbXAiOiAxNjIwNDU2OTg0OTA5fQ==', ['admin']))
