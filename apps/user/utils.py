import jwt
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData, SignatureExpired
from utils.constants import RET, Info_Map
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.authentication import jwt_decode_handler
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class AUTHERROR(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ('AUTHERROR')
    default_code = 401

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = {"msg": detail, "status": code}


# 自定义用户认证返回
class UserTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        # 采用drf获取token的手段 - HTTP_AUTHORIZATION - Authorization
        token = self.get_jwt_value(request)
        if token is None:
            return None
        # if not token:
        #     raise AUTHERROR(code=RET.NODATA, detail=Info_Map[RET.NODATA])
        # drf-jwt认证校验算法
        try:
            payload = jwt_decode_handler(token)
            # 如需要在这里可以进行校验密码,功能待定
        # 异常捕获
        except jwt.ExpiredSignature:
            raise AUTHERROR(code=RET.LOGINERR, detail=Info_Map[RET.LOGINERR])
        except jwt.InvalidTokenError:
            raise AUTHERROR(code=RET.SESSIONERR, detail=Info_Map[RET.SESSIONERR])
        except Exception as e:
            raise AUTHERROR(code=RET.SESSIONERR, detail=e)
        user = self.authenticate_credentials(payload)
        # 将认证结果drf
        return user, token


# 自定义签发
def generate_save_user_token(data):
    """
    生成保存用户数据的token
    :return: token
    """
    serializer = Serializer(settings.SECRET_KEY, 300)
    token = serializer.dumps(data)
    return token.decode()


# 自定义签发
def check_save_user_token(access_token):
    """
    检验保存用户数据的token
    :param token: token
    :return: data or None
    """
    serializer = Serializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(access_token)
    except BadData as e:
        return e
    except SignatureExpired:
        return 2
    else:
        return data


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功返回数据"""
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
        # 'user_role':user.role
    }


def jwt_response_payload_error_handler(serializer, request=None):
    return {
        "msg": "用户名或者密码错误",
        "status": RET.LOGINERR,
        "detail": serializer.errors
    }
