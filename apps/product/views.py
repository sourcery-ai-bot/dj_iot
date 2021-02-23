from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from utils.sql_sentences import *
from utils.constants import *
from utils.request_sidus import SQLHepler
from rest_framework.response import Response
from .serializers import ProdPartnerSerializer, ProdSerializer, FirmwareProdSerializer
from product.models import ProdPartner, FirmwareProduct
import requests
import base64
from user.models import User, Department
from django.utils.decorators import method_decorator
from user.serializers import UserSerializer, DepartmentSerializer
from itertools import groupby
from operator import itemgetter


class ProductList(GenericAPIView):
    """返回所有的产品信息"""
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request):
        user = request.user
        # 判断用户角色做不同处理
        user_roles = [role.get('id') for role in user.roles.values('id')]
        if min(user_roles) == 1:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            offered_list = [department.get('department_name') for department in serializer.data]
        else:
            offered_list = [department.get('department_name') for department in
                            user.department.values('department_name')]

        db_url = Sidus_Dev_Database

        res = []
        if offered_list:
            conn, cursor = SQLHepler.sql_multi_open(db_url)

            info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Product_Series_Client,
                                                 args=(offered_list,), cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
            if info:
                info.sort(key=itemgetter('offered_by'))
                for key, group in groupby(info, itemgetter('offered_by')):
                    offered_list.remove(key)
                    product_info = dict()
                    product_info['product_name'] = key
                    product_info['sub_series'] = []
                    series_info = list(group)
                    series_info.sort(key=itemgetter('product_series'), reverse=True)
                    product_series_list = []
                    for series_key, series_group in groupby(series_info, itemgetter('product_series')):
                        sub_pro = {}
                        if not series_key:
                            series_key = 'UNKNOWN'
                        product_series_list.append(series_key)
                        sub_pro['product_series'] = series_key
                        sub_pro['sub_info'] = list(series_group)
                        product_info['sub_series'].append(sub_pro)
                    # 每一个offered_by都确保有UNKNOWN
                    if 'UNKNOWN' not in product_series_list:
                        UNKNOWN_info = dict()
                        UNKNOWN_info.update(product_series='UNKNOWN', sub_info=[])
                        product_info['sub_series'].append(UNKNOWN_info)
                    res.append(product_info)

            if offered_list:
                for last_department in offered_list:
                    last_department_info = dict()
                    last_department_info['product_name'] = last_department
                    UNKNOWN_info = dict()
                    UNKNOWN_info.update(product_series='UNKNOWN', sub_info=[])
                    last_department_info['sub_series'] = [UNKNOWN_info]
                    res.append(last_department_info)
        else:
            return Response({"status": RET.DATAERR, "msg": Info_Map[RET.DATAERR]})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": res})


class ProductUuid(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        db_url = Sidus_Dev_Database

        conn, cursor = SQLHepler.sql_multi_open(db_url)
        data = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Product_UUID_Client, args=uuid, cursor=cursor)
        SQLHepler.close(conn=conn, cursor=cursor)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})


class HardWareProduct(GenericAPIView):
    """按需获取产品列表"""
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request, offered, series):
        user = request.user
        # 判断用户角色做不同处理
        user_roles = [role.get('id') for role in user.roles.values('id')]
        if min(user_roles) == 1:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            offered_list = [department.get('department_name') for department in serializer.data]
        else:
            offered_list = [department.get('department_name') for department in
                            user.department.values('department_name')]

        if offered == 'ALL':
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_All_Product_Client, args=(offered_list,),
                                                  db_dict=Sidus_Dev_Database)
        elif offered != 'ALL' and series == 'ALL':
            if offered not in offered_list:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_Product_Client, args=offered, db_dict=Sidus_Dev_Database)
        else:
            if offered not in offered_list:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_Product_offered_series_Client, args=(offered, series),
                                                  db_dict=Sidus_Dev_Database)
        info = []
        # 获取参与人员列表信息
        for data in hardware_p_info:
            uuid = data.get('uuid')
            instance = ProdPartner.objects.filter(pro_uuid=uuid)
            creator = None
            partner = []
            if instance:
                serializer = ProdPartnerSerializer(instance=instance, many=True)
                partner = serializer.data[0].get('pro_user')
                creator = serializer.data[0].get('pro_create')
                # if creator in partner:
                #     partner.remove(creator)
                # 获取创建者用户所在部门的高级用户
                try:
                    user = instance.first().pro_create
                    if user:
                        department_list = [c_user.get('id') for c_user in user.department.values('id')]
                        # 添加部门的高级人员到参与者
                        temp_list = User.objects.filter(department__in=department_list, roles=2)
                        for high_user in temp_list:
                            high_user_data = UserSerializer(instance=high_user).data
                            if high_user_data and high_user_data not in partner:
                                partner.append(high_user_data)
                except Exception as e:
                    return Response({"status": RET.UNKOWNERR, "msg": str(e)})
                if creator in partner:
                    partner.remove(creator)
            data.update(creator=creator, partner=partner)
            info.append(data)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": info})


class HardWareFirmware(APIView):
    """固件操作"""
    # permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        user = request.user
        uuid = uuid
        try:
            # status = self.get_user_permission(user, uuid)
            data = {}
            ctr = []
            dr = []
            ble = []
            ble_hardware_list = []
            db_url = Sidus_Dev_Database
            conn, cursor = SQLHepler.sql_multi_open(db_url)

            # 获取 基本信息
            firmware_infos = SQLHepler.sql_multi_fetch_all(SQL_Hardware_avail_Firmware_Client,
                                                           args=uuid, cursor=cursor)
            for info in firmware_infos:
                firmware_type = info.get('firmware_type')
                if firmware_type == 'Ctr':
                    res = self.get_firmware(info, uuid, cursor=cursor)
                    ctr.append(res)
                elif firmware_type == 'Dr':
                    res = self.get_firmware(info, uuid, cursor=cursor)
                    dr.append(res)
                elif firmware_type == 'Ble':
                    ble_hardware_version = info.get('hardware_version')
                    ble_hardware_list.append(ble_hardware_version)
                    res = self.get_firmware(info, uuid, cursor=cursor)
                    ble.append(res)

            # 处理蓝牙
            # 获取蓝牙的硬件版本
            ble_hardware_versions = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Ble_Firmware_Client,
                                                                  args=uuid, cursor=cursor)
            normal_ble_versions = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Ble_Firmware_Client,
                                                                args='normal', cursor=cursor)

            # 获取没有使用到的版本
            if ble_hardware_versions:
                for ble_version_info in ble_hardware_versions:
                    version = ble_version_info.get('hardware_version')
                    if version not in ble_hardware_list:
                        ble_hardware_list.append(version)
                        # 如果有对应的通用蓝牙,返回,没有,则为空
                        history_info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Firmware_Client,
                                                                     args=(uuid, version, 'Ble'),
                                                                     cursor=cursor)
                        # 获取通用蓝牙的信息
                        normal_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_Blue_Client_Version,
                                                                    args=version, cursor=cursor)
                        if not normal_info:
                            normal_info.update(hardware_version=version, normal_exist=0)
                        else:
                            normal_info.update(history=history_info, normal_exist=1)
                        ble.append(normal_info)

            # 如果没有蓝牙信息,添加所有通用蓝牙
            if normal_ble_versions:
                for normal_version_info in normal_ble_versions:
                    normal_version = normal_version_info.get('hardware_version')
                    if normal_version not in ble_hardware_list:
                        ble_hardware_list.append(normal_version)
                        # 获取所有通用蓝牙的信息
                        normal_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_Blue_Client_Version,
                                                                    args=normal_version, cursor=cursor)
                        if normal_info:
                            normal_info.update(normal_exist=1, history=[])
                            ble.append(normal_info)
            SQLHepler.close(conn=conn, cursor=cursor)
        except Exception as e:
            return Response({"msg": str(e)})
        # 构建输出数据结构
        # data['partake_status'] = status
        data['Ctr'] = ctr
        data['Dr'] = dr
        data['Ble'] = ble
        with open("./test_product.txt",'w') as f:
            f.write(str(data))
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})

    @staticmethod
    def get_user_permission(user, uuid):
        # 判定用户是否参与\ 1参与
        roles = [role_names['id'] for role_names in user.roles.all().values('id')]
        if not roles:
            return 0
        if min(roles) == 1:
            return 1
        # 获取参与者列表
        user_ids = [dic_id.get('pro_user') for dic_id in
                    ProdPartner.objects.filter(pro_uuid=uuid).values('pro_user')]

        if user.id in user_ids:
            return 1

        product_instance = ProdPartner.objects.filter(pro_uuid=uuid).first()

        if product_instance:
            # 找到部门
            creator = product_instance.pro_create
            if creator:
                department_list = [c_user.get('id') for c_user in creator.department.values('id')]
                temp_list = User.objects.filter(department__in=department_list, roles=2)
                # 不是创建者且不是创建者的高级用户，直接返回0
                if user != creator and user not in temp_list:
                    return 0
                else:
                    return 1
            else:
                return 0
        # 没有使用记录,直接为０
        else:
            return 0

    @staticmethod
    def get_firmware(info, uuid, cursor):
        h_version = info.get('hardware_version')
        h_type = info.get('firmware_type')
        history_info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Firmware_Client,
                                                     args=(uuid, h_version, h_type),
                                                     cursor=cursor)
        if h_type == 'Ble':
            infos = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Firmware_Blue_Client_Version, h_version, cursor=cursor)
            if infos:
                info.update(normal_exist=1)
            else:
                info.update(normal_exist=0)
        info.update(history=history_info)
        return info

    def post(self, request, uuid):
        if uuid == 'add':
            user = request.user
            data = request.data.copy()
            ctr_info = data.get('Ctr')
            dr_info = data.get('Dr')
            ble_info = data.get('Ble')
            ble_status = data.get('Ble_status')
            uuid_ascii_code = data.get('uuid_ascii_code')

            if not uuid_ascii_code:
                return Response({"status": RET.PARAMERR, "msg": 'UUID CAN NOT BE NONE'})
            # 如果存在,判定用户是不是在列表
            instance = ProdPartner.objects.filter(pro_uuid=uuid_ascii_code).first()
            # 保存用户数据到本地db
            # 如果不存在,新增的时候，添加用户数据到本地
            if not instance:
                department_list = [c_user.get('id') for c_user in user.department.values('id')]
                # 添加部门的高级人员到参与者
                user_high_list = [temp.get('id') for temp in
                                  User.objects.filter(department__in=department_list, roles=2).values('id')]
                info = {
                    "pro_uuid": uuid_ascii_code,
                    "pro_user": user_high_list,
                    "pro_create": user.id
                }
                serializer = ProdSerializer(data=info)
                try:
                    serializer.is_valid(raise_exception=True)
                except Exception as e:
                    return Response({"status": RET.PARAMERR, "msg": str(e)})
                serializer.save()
            # 处理数据
            db_url = Sidus_Dev_Database
            conn, cursor = SQLHepler.sql_multi_open(db_url)
            try:
                if ctr_info:
                    ctr_info.update(firmware_normal=0)
                    self.insert_data(user, cursor, **ctr_info)
                if dr_info:
                    dr_info.update(firmware_normal=0)
                    self.insert_data(user, cursor, **dr_info)
                if ble_status:
                    if int(ble_status) == 1:
                        # 使用自定义蓝牙
                        if ble_info:
                            ble_info.update(firmware_normal=0)
                            self.insert_data(user, cursor, **ble_info)

                # 更新当前的产品的使用状态product_status = 1
                SQLHepler.sql_multi_execute(SQL_Status_Product, args=uuid_ascii_code, cursor=cursor)
                updated_name = user.first_name + " " + user.last_name
                SQLHepler.sql_multi_execute(SQL_Status_Product_Admin, args=(updated_name, uuid_ascii_code),
                                            cursor=cursor)
                SQLHepler.close(conn=conn, cursor=cursor)
            except ValueError as e:
                conn.rollback()
                return Response({"status": RET.ROLEERR, "msg": str(e)})
            except Exception as e:
                # 进行回滚操作
                conn.rollback()
                return Response({"status": RET.PARAMERR, "msg": str(e)})

            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def put(self, request, uuid):
        firmware_id = uuid
        data = request.data.copy()
        user = request.user
        db_url = Sidus_Dev_Database
        conn, cursor = SQLHepler.sql_multi_open(db_url)

        firmware_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, args=firmware_id, cursor=cursor)
        firmware_uuid = firmware_info.get('uuid_ascii_code')
        if not firmware_uuid:
            SQLHepler.close(conn=conn, cursor=cursor)
            return Response({"status": RET.FIRMWARNOTEXIST, "msg": Info_Map[RET.FIRMWARNOTEXIST]})
            # 判断用户是否参与
        if not self.get_user_permission(user, firmware_uuid):
            return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})
        # 更新最后更新人员
        data.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, id=firmware_id)
        firmware_file = data.get('firmware_url')
        if firmware_file:
            try:
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_with_file, data, cursor=cursor)
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            try:
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_without_file, data, cursor=cursor)
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": str(e)})
        SQLHepler.close(conn=conn, cursor=cursor)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def insert_data(self, user, cursor, **kwargs):
        uuid_ascii_code = kwargs.get('uuid_ascii_code')
        firmware_type = kwargs.get('firmware_type')
        hardware_version = kwargs.get('hardware_version')
        firmware_version = kwargs.get('firmware_version')

        # uuid_ascii_code 是否存在
        if not uuid_ascii_code:
            raise Exception('uuid不能为空')

        # 查询是否已经有存在
        res = SQLHepler.sql_multi_fetch_one(SQL_Update_Hardware_Firmware_Exist,
                                            (uuid_ascii_code, firmware_type, hardware_version, firmware_version),
                                            cursor=cursor)
        if int(res.get('count')) >= 1:
            # 更新数据
            # 判断用户是否参与
            # user_ids = [dic_id.get('pro_user') for dic_id in
            #             ProdPartner.objects.filter(pro_uuid=uuid_ascii_code).values('pro_user')]
            # # 不是管理员且没参与，直接返回
            # product_instance = ProdPartner.objects.filter(pro_uuid=uuid_ascii_code).first()
            # if product_instance:
            #     # 找到部门
            #     creator = product_instance.pro_create
            #     # 找到部门
            #     department_list = [c_user.get('id') for c_user in creator.department.values('id')]
            #
            #     # 添加部门的高级人员到参与者
            #     temp_list = User.objects.filter(department__in=department_list, roles=2)
            #
            #     roles = [role_names['id'] for role_names in user.roles.all().values('id')]
            #
            #     if user != creator and user.id not in user_ids and user not in temp_list and min(roles) != 1:
            #         raise ValueError('用户角色错误')
            if not self.get_user_permission(user, uuid_ascii_code):
                return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})
            # 更新最后更新人员
            firmware_id = res.get('id')
            kwargs.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, id=firmware_id)
            firmware_file = kwargs.get('firmware_url')
            # 判断是否更新文件
            if firmware_file:
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_with_file, kwargs, cursor=cursor)
            else:
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_without_file, kwargs, cursor=cursor)

        else:
            # 更新其他固件版本的available
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_available,
                                        (uuid_ascii_code, firmware_type, hardware_version), cursor=cursor)
            # 补充数据,插入新数据
            kwargs.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, firmware_status=0)
            SQLHepler.sql_multi_execute(SQL_Insert_Hardware_Firmware, kwargs, cursor=cursor)


class UploadFile(APIView):
    """上传文件,修改后以列表传输文件和数据firmware_type:[],firmware_file[],索引一一对应"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """上传文件"""
        user = request.user
        sidus_token = user.sidus_token
        header = {
            'Token-Data': sidus_token
        }
        firmware_type = request.data.get('firmware_type')
        firmware_b64 = request.data.get('firmware_file')

        if len(firmware_type) != len(firmware_b64):
            return Response({"status": RET.PARAMERR, "msg": "Type And File Not equal"})
        # 遍历数据，上传文件
        data = {}
        status_list = []
        type_list = []
        try:
            for temp in zip(firmware_type, firmware_b64):
                if temp[1]:
                    if temp[0] not in ['Ctr', 'Ble', 'Dr']:
                        return Response({"status": RET.PARAMERR, "msg": "Type Must Be 'Ctr','Ble' Or 'Dr'"})
                    file_64 = temp[1].split(',')[-1].strip()
                    firmware_file = base64.b64decode(file_64)

                    file = {'upload_file': firmware_file}
                    res = requests.post(S3_upload_url, data={"file_type": temp[0]}, files=file, headers=header).json()
                    firmware_size = res.get('size')
                    firmware_url = res.get('object_key')
                    status = res.get('status')
                    msg = res.get('msg')
                else:
                    firmware_size = 0
                    firmware_url = ""
                    status = RET.NODATA
                    msg = Info_Map[RET.NODATA]

                data[temp[0]] = {'firmware_size': firmware_size, 'firmware_url': firmware_url, 'status': status,
                                 'msg': msg}
                # 判断上传状态
                if int(status) not in status_list:
                    status_list.append(int(status))
                    type_list.append(temp[0])
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": str(e)})

        if len(status_list) == 1:
            if status_list[0] == 200:
                # 全部上传成功
                data.update(status=status_list[0], msg='ALL SUCCESS')
            else:
                # 全部失败
                data.update(status=status_list[0], msg='ALL FAILURE')
        else:
            # 部分失败
            if 200 in status_list:
                index = status_list.index(200)
                type_list.pop(index)
                data.update(status=RET.FILEUPLOADERR, msg='{} FAILURE'.format(",".join(type_list)))
            else:
                # 全部失败
                data.update(status=status_list[0], msg='ALL FAILURE')
        return Response(data)


class ClientSearchView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request, info):
        user = request.user
        user_roles = [role.get('id') for role in user.roles.values('id')]
        if min(user_roles) == 1:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            department_list = [department.get('department_name') for department in serializer.data]
        else:
            department_list = [department.get('department_name') for department in
                               user.department.values('department_name')]

        res = SQLHepler.fetch_all(SQL_Hardware_Product_Search_Client.format(info, info, info, info, department_list),
                                  db_dict=Sidus_Dev_Database)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": res})


class OperateFirmwareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """启用某个固件"""
        data = request.data.copy()
        user = request.user
        uuid_ascii_code = data.get('uuid_ascii_code')
        firmware_type = data.get('firmware_type')
        hardware_version = data.get('hardware_version')
        # 判断用户是否参与
        if not self.get_user_permission(user, uuid_ascii_code):
            return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})

        # 更新其他驱动信息
        try:
            # 更新其他固件版本的available状态
            db_url = Sidus_Dev_Database
            conn, cursor = SQLHepler.sql_multi_open(db_url)
            if firmware_type not in ['Ctr', 'Ble', 'Dr']:
                return Response({"status": RET.PARAMERR, "msg": "Type Must Be 'Ctr','Ble' Or 'Dr'"})
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_available,
                                        (uuid_ascii_code, firmware_type, hardware_version), cursor=cursor)

            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_able, id,
                                        cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    @staticmethod
    def get_user_permission(user, uuid):
        # 判定用户是否参与\ 1参与
        roles = [role_names['id'] for role_names in user.roles.all().values('id')]
        if not roles:
            return 0
        if min(roles) == 1:
            return 1
        # 获取参与者列表
        user_ids = [dic_id.get('pro_user') for dic_id in
                    ProdPartner.objects.filter(pro_uuid=uuid).values('pro_user')]

        if user.id in user_ids:
            return 1

        product_instance = ProdPartner.objects.filter(pro_uuid=uuid).first()

        if product_instance:
            # 找到部门
            creator = product_instance.pro_create
            if creator:
                department_list = [c_user.get('id') for c_user in creator.department.values('id')]
                temp_list = User.objects.filter(department__in=department_list, roles=2)
                # 不是创建者且不是创建者的高级用户，直接返回0
                if user != creator and user not in temp_list:
                    return 0
                else:
                    return 1
            else:
                return 0
        # 没有使用记录,直接为０
        else:
            return 0


class BackNormalBleView(APIView):
    """恢复通用蓝牙"""
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        user = request.user
        firmware_type = request.data.get('firmware_type')
        # 判断用户是否参与
        if not self.get_user_permission(user, uuid):
            return Response({"status": RET.ROLEERR, "msg": Info_Map[RET.ROLEERR]})
        # 判断回退是否蓝牙
        if firmware_type != 'Ble':
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        hardware_version = request.data.get('hardware_version')

        if not hardware_version:
            return Response({"status": RET.PARAMERR, "msg": '必须指明通用蓝牙版本'})

        db_url = Sidus_Dev_Database

        conn, cursor = SQLHepler.sql_multi_open(db_url)

        try:
            # self.insert_normal_blue(cursor, user, uuid, hardware_version)
            # 更新当前的硬件驱动版本的available
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_available,
                                        (uuid, firmware_type, hardware_version), cursor)

            SQLHepler.close(conn=conn, cursor=cursor)
        except ValueError as e:
            SQLHepler.close(conn=conn, cursor=cursor)
            return Response({"status": RET.PARAMERR, "msg": str(e)})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    @staticmethod
    def get_user_permission(user, uuid):
        # 判定用户是否参与\ 1参与
        roles = [role_names['id'] for role_names in user.roles.all().values('id')]
        if not roles:
            return 0
        if min(roles) == 1:
            return 1
        # 获取参与者列表
        user_ids = [dic_id.get('pro_user') for dic_id in
                    ProdPartner.objects.filter(pro_uuid=uuid).values('pro_user')]

        if user.id in user_ids:
            return 1

        product_instance = ProdPartner.objects.filter(pro_uuid=uuid).first()

        if product_instance:
            # 找到部门
            creator = product_instance.pro_create
            if creator:
                department_list = [c_user.get('id') for c_user in creator.department.values('id')]
                temp_list = User.objects.filter(department__in=department_list, roles=2)
                # 不是创建者且不是创建者的高级用户，直接返回0
                if user != creator and user not in temp_list:
                    return 0
                else:
                    return 1
            else:
                return 0
        # 没有使用记录,直接为０
        else:
            return 0


class CheckNormalExistedView(APIView):
    """检测通用蓝牙固件是否存在"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        db_url = Sidus_Dev_Database
        conn, cursor = SQLHepler.sql_multi_open(db_url)
        status = 0
        infos = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Firmware_Blue_Client, cursor=cursor)
        if infos:
            status = 1
        SQLHepler.close(conn=conn, cursor=cursor)
        data = dict()
        data.update(status=status)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})


from apps.management.views import PartnerView
from utils.decorates import partnercheck, rolescheck


class ClientPaternerView(PartnerView):
    """用户添加参与者"""
    permission_classes = [IsAuthenticated]

    # @method_decorator(partnercheck)
    # def post(self, request):
    #     info = request.data.copy()
    #     uuid = info.get('pro_uuid')
    #     user_ids = info.get('pro_user')
    #     instance = ProdPartner.objects.filter(pro_uuid=uuid).first()
    #     if not instance:
    #         return Response({"status": RET.PARAMERR, "msg": "当前产品不存在"})
    #     # 获取所有的id
    #     if instance.pro_create:
    #         creator_id = instance.pro_create.id
    #         if creator_id in user_ids:
    #             user_ids.remove(creator_id)
    #
    #     instance.pro_user = user_ids
    #     instance.save()
    #     return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    # @method_decorator(partnercheck)
    # def delete(self, request):
    #     info = request.data
    #     user_ids = info.get('pro_user')
    #     uuid = info.get('pro_uuid')
    #     instance = ProdPartner.objects.filter(pro_uuid=uuid).first()
    #     for user_id in user_ids:
    #         instance.pro_user.remove(user_id)
    #     return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class ClientFirmwareProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FirmwareProdSerializer
    queryset = FirmwareProduct.objects.all()

    # @method_decorator(rolescheck)
    def post(self, request):
        data = request.data.copy()
        user = request.user
        user_name = user.first_name + " " + user.last_name
        data.update(product_updated_admin_name=user_name, submit_user=user.id)
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": str(e)})
        serializer.save()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


from apps.management.views import UserView


class ClientUser(UserView):
    """客户人员获取所有用户信息"""
    permission_classes = [IsAuthenticated]
