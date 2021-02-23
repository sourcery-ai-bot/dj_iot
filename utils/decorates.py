# from guardian.decorators import permission_required
from rest_framework.response import Response
from functools import wraps
from .constants import RET, Info_Map
from product.models import ProdPartner


# 用户添加参与人员检测
def partnercheck(func):
    @wraps(func)
    def wrappers(request, *args, **kwargs):
        user = request.user
        uuid = request.data.get('pro_uuid')
        instance = ProdPartner.objects.filter(pro_uuid=uuid).first()
        roles = [role_names['id'] for role_names in user.roles.all().values('id')]
        # 当最小的角色id大于3,认定为普通该用户,且不是创建者
        if min(roles) >= 3 and user != instance.pro_create:
            return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})

        return func(request, *args, **kwargs)
    return wrappers


# 用户添加产品检测
def rolescheck(func):
    @wraps(func)
    def wrappers(request, *args, **kwargs):
        user = request.user
        roles = [role_names['id'] for role_names in user.roles.all().values('id')]
        # 当最小的角色id大于3,认定为普通该用户
        if min(roles) >= 3:
            return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})

        return func(request, *args, **kwargs)

    return wrappers
