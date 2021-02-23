import requests
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from utils.request_sidus import client_post_mutipart_formdata_requests
from utils.constants import *
from utils.request_sidus import SQLHepler
from user.models import User, RequestInfo
from .serializers import CreateUserSerializer, UpdateUserSerializer, UserSerializer, UpdateUserPWDSerializer, \
    RequestSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from utils.sql_sentences import SQL_User_info
from management.views import DepartmentsView
import base64


class UserLoginView(APIView):
    """
    用户登录
    """

    def post(self, request):
        info = request.data.copy()
        email = info.get('username', None)
        password = info.get('password', None)
        verification_code = info.get('verification_code', None)
        info_dict = {
            'email': email,
            'password': password,
            'verification_code': verification_code
        }
        response_data = client_post_mutipart_formdata_requests(Sidus_Pro_LoginUrl, info_dict)
        response_status = response_data.get('status', '')
        msg = response_data.get('msg', '')
        if str(response_status) == '200':
            # 获取Sidus信息
            sidus_user_token = response_data.get('token', '')
            sidus_user_id = response_data.get('user_id', '')
            user_info = SQLHepler.fetch_one(SQL_User_info, args=sidus_user_id, db_dict=Sidus_Pro_Database)
            # 获取头像信息
            if user_info['sidus_avatar']:
                user_info['sidus_avatar'] = S3_image_url + user_info['sidus_avatar']
            info.update(sidus_id=sidus_user_id, sidus_token=sidus_user_token, email=email, **user_info)
            user = User.objects.filter(username=email).first()
            # 没有此用户,则创建本地用户
            if user is None:
                serializer = CreateUserSerializer(data=info)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    user = User.objects.get(username=email)
                except Exception as e:
                    return Response({"status": RET.SERVERERR, "msg": str(e)})
            else:
                # 如果存在当前用户，则更新数据
                User.objects.filter(username=email).update(sidus_token=sidus_user_token,
                                                           sidus_id=sidus_user_id,
                                                           email=email,
                                                           sidus_avatar=user_info.get('sidus_avatar'))
                user = User.objects.get(username=email)

                # user check_pwd 用户密码检验功能
                # 待定
            # 生成token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            # 生成token进行返回
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "token": token})
        elif int(response_status) == 4002:
            return Response({"status": RET.PWDERR, "msg": Info_Map[RET.PWDERR]})
        elif int(response_status) == 4003:
            return Response({"status": RET.VERIFYCODEERR, "msg": Info_Map[RET.VERIFYCODEERR]})
        elif int(response_status) == 4103:
            return Response({"status": RET.DATAERR, "msg": Info_Map[RET.DATAERR]})
        elif int(response_status) == 4001:
            return Response({"status": RET.USERERR, "msg": Info_Map[RET.USERERR]})
        else:
            return Response({"status": RET.PARAMERR, "msg": msg})


class UserRegEmailView(APIView):
    """
    用户注册邮件,调用
    """

    def post(self, request):
        print(1)
        info = request.data
        response_data = client_post_mutipart_formdata_requests(Sidus_Pro_ReEmailUrl, info)
        response_status = response_data.get('status', '')
        if str(response_status) == '200':
            return Response({"status": RET.OK, "msg": response_data.get('msg')})

        elif str(response_status) == '403':
            return Response({"status": RET.DATAEXIST, "msg": Info_Map[RET.DATAEXIST]})

        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


class UserRegisterView(APIView):
    """
    用户注册，调用，并在本地保存
    """

    def post(self, request):
        info = request.data.copy()
        info_dict = {
            'username': info.get('email', None),
            'password': info.get('password', None),
            'first_name': info.get('first_name', None),
            'last_name': info.get('last_name', None),
            'email': info.get('email', None),
            'avatar_color': info.get('avatar_color', None)
        }
        info.update(occupation='16')
        response_data = client_post_mutipart_formdata_requests(Sidus_Pro_RegisterUrl, info)
        response_status = response_data.get('status', '')
        if str(response_status) == '200':
            # 保存数据到本地
            serializer = CreateUserSerializer(data=info_dict)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            except Exception as e:
                return Response({"status": RET.PARAMLOST, "msg": e})
        else:
            return Response({"status": response_status, "msg": response_data.get('msg')})


class VerifyRegInfo(APIView):
    """调用，校验邮箱注册验证码"""

    def post(self, request):
        print(1)
        info = request.data
        response_data = client_post_mutipart_formdata_requests(Sidus_Pro_Veridy_Reg, info)
        response_status = response_data.get('status', '')
        if str(response_status) == '200':
            return Response({"status": RET.OK, "msg": response_data.get('msg')})

        elif str(response_status) == '400':
            return Response({"status": RET.VERIFYCODEERR, "msg": Info_Map[RET.VERIFYCODEERR]})

        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


# 更改用户信息
class ChangeUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user_id = request.user.sidus_id
        sidus_token = request.user.sidus_token
        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not (first_name and last_name):
            return Response({"status": RET.PARAMLOST, "msg": Info_Map[RET.PARAMLOST]})
        info = {
            'first_name': first_name,
            'last_name': last_name
        }
        avatar_url = request.data.get('avatar')
        if avatar_url:
            info.update(sidus_avatar=avatar_url)
            # 更新头像数据到线上服务器
            status, msg = self.post_sidus_avatar(sidus_token, user_id, avatar_url)
            if int(status) != 200:
                return Response({"status": status, "msg": msg})
            # 更新图片带S3CDN操作
            info.update(sidus_avatar=S3_image_url + avatar_url)

        # 更新线上的用户信息
        status, msg = self.update_sidus_info(sidus_token, first_name, last_name)
        if int(status) != 200:
            return Response({"status": status, "msg": msg})
        # 更新本地数据
        instance = self.get_object()
        serializer = self.get_serializer(data=info, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if info.get('sidus_avatar'):
            s3_url = info.get('sidus_avatar')
            info.update(sidus_avatar=s3_url)
        else:
            info.update(sidus_avatar='')
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], 'info': info})

    @staticmethod
    def upload_avatar(sidus_token, file):
        header = {
            'Token-Data': sidus_token
        }
        file = {'upload_file': file}
        res = requests.post(S3_upload_url, data={"file_type": 'USERICON'}, files=file, headers=header).json()
        avatar_url = res.get('object_key')
        status = res.get('status')
        msg = res.get('msg')
        return avatar_url, status, msg

    @staticmethod
    def post_sidus_avatar(sidus_token, fk_user, avatar_url):
        header = {
            'Token-Data': sidus_token
        }
        data = {
            'fk_user': fk_user,
            'icon_file': avatar_url
        }
        res = requests.post(Sidus_Pro_Post_avatar, data=data, headers=header).json()
        status = res.get('status')
        msg = res.get('msg')
        return status, msg

    @staticmethod
    def update_sidus_info(sidus_token, first_name, last_name):
        header = {
            'Token-Data': sidus_token
        }
        data = {
            'first_name': first_name,
            'last_name': last_name
        }
        res = requests.post(Sidus_Pro_Post_User_info, data=data, headers=header).json()
        status = res.get('status')
        msg = res.get('msg')
        return status, msg


# 更改用户信息
class ChangeUserAvatar(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        sidus_token = request.user.sidus_token
        avatar = request.FILES.get('avatar')
        if avatar:
            avatar_url, status, msg = self.upload_avatar(sidus_token=sidus_token, file=avatar)
        else:
            return Response({"status": RET.PARAMLOST, "msg": Info_Map[RET.PARAMLOST]})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], 'info': avatar_url})

    @staticmethod
    def upload_avatar(sidus_token, file):
        header = {
            'Token-Data': sidus_token
        }
        file = {'upload_file': file}
        res = requests.post(S3_upload_url, data={"file_type": 'USERICON'}, files=file, headers=header).json()
        avatar_url = res.get('object_key')
        status = res.get('status')
        msg = res.get('msg')
        return avatar_url, status, msg

    @staticmethod
    def post_sidus_avatar(sidus_token, fk_user, avatar_url):
        header = {
            'Token-Data': sidus_token
        }
        data = {
            'fk_user': fk_user,
            'icon_file': avatar_url
        }
        res = requests.post(Sidus_Pro_Post_avatar, data=data, headers=header).json()
        status = res.get('status')
        msg = res.get('msg')
        return status, msg

    @staticmethod
    def update_sidus_info(sidus_token, first_name, last_name):
        header = {
            'Token-Data': sidus_token
        }
        data = {
            'first_name': first_name,
            'last_name': last_name
        }
        res = requests.post(Sidus_Pro_Post_User_info, data=data, headers=header).json()
        status = res.get('status')
        msg = res.get('msg')
        return status, msg


# 获取用户信息
class UserInfoView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        info = serializer.data
        request_departments = []
        try:
            status = self.get_object().request_info.status
        except Exception as e:
            status = -1

        if status != -1:
            request_departments = self.get_object().request_info.department.split('/')

        info.update(status=status, request_departments=request_departments)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": info})


# 用户更改密码
class UserChangePWD(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserPWDSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        info = request.data
        sidus_token = request.user.sidus_token
        header = {
            'Token-Data': sidus_token
        }
        password = info.get('password')
        password_commit = info.get('password_commit')
        verification_code = info.get('verification_code')

        if not (password and verification_code):
            return Response({"status": RET.PARAMLOST, "msg": Info_Map[RET.PARAMLOST]})

        if password != password_commit:
            return Response({"status": RET.PWDCOMMITERR, "msg": Info_Map[RET.PWDCOMMITERR]})
        # 调用接口,更改线上账号密码
        data = {
            'new_password': password,
            'verification_code': verification_code
        }
        res = requests.post(Sidus_Pro_ChangePWD, data=data, headers=header).json()

        if int(res.get('status')) == 200:
            # 更改本地密码
            instance = self.get_object()
            local_info = {'password': password}
            serializer = self.get_serializer(data=local_info, instance=instance)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                return Response({"status": RET.PWDTYPEERR, "msg": str(e)})
            serializer.save()
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        else:
            return Response({"status": res.get('status'), "msg": res.get('msg')})


# 获取更改密码的验证码
class UserPWDEMAILView(APIView):
    """
    用户修改密码验证码,调用
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sidus_token = request.user.sidus_token
        header = {
            'Token-Data': sidus_token
        }
        info = request.data
        email = info.get('email')
        if not email:
            return Response({"status": RET.PARAMLOST, "msg": Info_Map[RET.PARAMLOST]})
        response_data = requests.post(Sidus_Pro_ChangePWDEmail, data=info, headers=header).json()
        if int(response_data.get('status')) == 200:
            return Response({"status": RET.OK, "msg": response_data.get('msg')})
        else:
            return Response({"status": response_data.get('status'), "msg": response_data.get('msg')})


# 获取邮箱登录的验证码
class EmailLoginView(APIView):
    """
    用户邮箱验证码,调用
    """

    def post(self, request):
        info = request.data
        email = info.get('email')
        if not email:
            return Response({"status": RET.PARAMLOST, "msg": Info_Map[RET.PARAMLOST]})
        response_data = requests.post(Sidus_Pro_EmailLogin, data=info).json()
        if int(response_data.get('status')) == 200:
            return Response({"status": RET.OK, "msg": response_data.get('msg')})
        else:
            return Response({"status": response_data.get('status'), "msg": response_data.get('msg')})


# 用户申请获取所有部门
class UserDepartmentsView(DepartmentsView):
    permission_classes = [IsAuthenticated]


# 用户发送申请
class UserRequetView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestSerializer
    queryset = RequestInfo.objects.all()

    def post(self, request):
        user = request.user
        info = request.data.copy()
        # 避免恶意上传数据
        if info.get('status'):
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        info.update(user=user.id)
        if self.get_object():
            return Response({"status": RET.PARAMERR, "msg": 'Request Exists,Please Wait'})
        serializer = self.get_serializer(data=info)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def get_object(self):
        return self.queryset.filter(user=self.request.user.id).first()

    def put(self, request):
        """再次申请"""
        info = request.data.copy()
        # 避免恶意上传数据
        if info.get('status'):
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        info.update(status=0)
        serializer = self.get_serializer(data=info, instance=self.get_object())
        try:
            serializer.is_valid(raise_exception=True)

        except Exception as e:
            return Response({"status": RET.PWDTYPEERR, "msg": str(e)})
        serializer.save()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class UserDel(APIView):

    def get(self, request, email):
        instance = User.objects.filter(username=email).first()
        if not instance:
            return Response({"status": RET.USERERR, "msg": '用户不存在'})
        print(instance.email)
        x = instance.delete()
        print(x)
        return Response({"status": RET.OK, "msg": 'Delete success'})
