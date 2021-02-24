from rest_framework.views import exception_handler as drf_exception_handler
import logging
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status
from utils.constants import RET, Info_Map
from pymysql.err import OperationalError

# 获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('iot_error')


def exception_handler(exc, context):
    """
    自定义异常处理
    :param exc: 异常
    :param context: 抛出异常的上下文
    :return: Response响应对象
    """
    # 调用drf框架原生的异常处理方法
    response = drf_exception_handler(exc, context)

    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, OperationalError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'msg': '服务器内部错误', 'status': 4500}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
    elif response.status_code == 400:
        response = Response({'msg': Info_Map[RET.PARAMERR], 'status': RET.PARAMERR}, status=status.HTTP_400_BAD_REQUEST)

    elif response.status_code == 401:
        if response.data.get('status'):
            response = Response({'msg': response.data.get('msg'), 'status': response.data.get('status')},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = Response({'msg': response.data.get('detail'), 'status': RET.PARAMERR},
                                status=status.HTTP_401_UNAUTHORIZED)

    elif response.status_code == 403:
        response = Response({'msg': Info_Map[RET.ROLEPEMIT], 'status': RET.ROLEPEMIT},
                            status=status.HTTP_403_FORBIDDEN)
    return response
