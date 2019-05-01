from itsdangerous import TimedJSONWebSignatureSerializer as Seriallizer
from django.conf import settings

# 要求是字典
def dumps(json, expire):
    #创建对象，
    #setting.SECRET_KEY 是个密钥
    serializer = Seriallizer(settings.SECRET_KEY, expire)
    # 他是beytes
    #进行加密
    token = serializer.dumps(json)
    #返回字符串
    return token.decode()


def loads(token,expire):
    #c创建对象
    serializer=Seriallizer(settings.SECRET_KEY,expire)
    try:
        #进行解密
        json=serializer.loads(token)
    except:
        #如果字符串被修改或者过期则会返回none
        return None
    else:
        #返回字典
        return json

