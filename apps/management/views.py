from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from utils.constants import *
from utils.request_sidus import SQLHepler
from rest_framework.response import Response
from user.serializers import UserSerializer, RoleSerializer, ManageUpdateUserSerializer, ManageDepartmentSerializer, \
    DepartmentSerializer
from user.models import User, Role, Department, RequestInfo
import requests
from utils.sql_sentences import *
from product.models import ProdPartner, FirmwareProduct
from product.serializers import ProdSerializer, ProdPartnerSerializer, FirmwareProdSerializer
from itertools import groupby
from operator import itemgetter


class UserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.filter(request_info__status=1)

    def get(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})


class RoleUserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.filter().exclude(username='AnonymousUser')

    def get(self, request, role):
        if role == 'ALL':
            instance = self.get_queryset().filter(request_info__status=1)
        elif role == 'undistributed':
            instance = self.get_queryset().filter(roles=None)
        else:
            role = Role.objects.filter(id=role).first()
            if not role:
                return Response({"status": RET.ROLENOTEXIST, "msg": Info_Map[RET.ROLENOTEXIST]})
            instance = self.get_queryset().filter(roles=role.id)
        serializer = self.get_serializer(instance, many=True)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})


class RoleListView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RoleSerializer
    queryset = Role.objects.all()

    def get(self, request):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})


class DepartmentsView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})


class DepartmentListView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ManageDepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request, department):
        if department == 'ALL':
            instance = self.get_queryset()
            serializer = self.get_serializer(instance, many=True)
        else:
            instance = self.get_queryset().filter(id=department).first()
            if not instance:
                return Response({"status": RET.DEPARTMENTNOTEXIST, "msg": Info_Map[RET.DEPARTMENTNOTEXIST]})

            serializer = self.get_serializer(instance)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})

    def delete(self, request, department):
        instance = self.get_queryset().filter(id=department).first()

        if not instance:
            return Response({"status": RET.DEPARTMENTNOTEXIST, "msg": Info_Map[RET.DEPARTMENTNOTEXIST]})

        if instance.id <= 4:
            return Response({"status": RET.ROLEPEMIT, "msg": Info_Map[RET.ROLEPEMIT]})

        # 更新当前用户的部门到Others部门下
        others = Department.objects.filter(department_name='Others').first()
        if not others:
            return Response({"status": RET.DEPARTMENTNOTEXIST, "msg": Info_Map[RET.DEPARTMENTNOTEXIST]})

        for user in instance.users.all():
            # 判断用户是多部门还是单部门
            if len(user.department.all().values('id')) <= 1:
                user.department = [others.id]
                user.save()
            else:
                user.department.remove(department)

        instance.delete()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def post(self, request, department):
        if department == "add":
            data = request.data
            try:
                serializer = DepartmentSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except Exception as e:
                return Response({"status": RET.DEPARTMENTEXIST, "msg": Info_Map[RET.DEPARTMENTEXIST]})
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def put(self, request, department):
        if department == "update":
            data = request.data
            department_id = data.get('department_id')
            department_name = data.get('department_name')
            department_instance = self.queryset.filter(id=department_id).first()
            department_instance.department_name = department_name
            department_instance.save()
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


class UpdateUserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ManageUpdateUserSerializer
    queryset = User.objects.all()
    lookup_field = 'pk'

    def put(self, request, pk):
        data = request.data

        serializer = self.get_serializer(data=data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        roles = data.get('roles')
        if 1 in roles:
            user = User.objects.filter(id=pk).first()
            user.is_staff = 1
            user.save()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def delete(self, request, pk):
        instance = self.get_object()
        instance.delete()

        email = instance.username
        url = Sidus_Dev_Delete_User.format(email)
        requests.delete(url)
        return Response({"status": RET.OK, "msg": "DELETE OK"})


class ManageProductList(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request, env):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        department_list = [department.get('department_name') for department in serializer.data]

        if env == 'pro':
            db_url = Sidus_Pro_Database
        else:
            db_url = Sidus_Dev_Database
        res = []
        if department_list:
            conn, cursor = SQLHepler.sql_multi_open(db_url)
            info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Product_Series,
                                                 args=(department_list,), cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
            info.sort(key=itemgetter('offered_by'))
            for key, group in groupby(info, itemgetter('offered_by')):
                department_list.remove(key)
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
                print(product_series_list)
                if 'UNKNOWN' not in product_series_list:
                    UNKNOWN_info = dict()
                    UNKNOWN_info.update(product_series='UNKNOWN', sub_info=[])
                    product_info['sub_series'].append(UNKNOWN_info)
                res.append(product_info)

            if department_list:
                for last_department in department_list:
                    last_department_info = dict()
                    last_department_info['product_name'] = last_department
                    UNKNOWN_info = dict()
                    UNKNOWN_info.update(product_series='UNKNOWN', sub_info=[])
                    last_department_info['sub_series'] = [UNKNOWN_info]
                    res.append(last_department_info)
        else:
            return Response({"status": RET.DATAERR, "msg": Info_Map[RET.DATAERR]})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": res})


class ManageProductListCreated(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get(self, request, env):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        department_list = [department.get('department_name') for department in serializer.data]

        if env == 'pro':
            db_url = Sidus_Pro_Database
        else:
            db_url = Sidus_Dev_Database
        res = []
        conn, cursor = SQLHepler.sql_multi_open(db_url)
        info = SQLHepler.sql_multi_fetch_all(SQL_Created_Hardware_Product_Series,
                                             args=(department_list,), cursor=cursor)
        SQLHepler.close(conn=conn, cursor=cursor)
        info.sort(key=itemgetter('offered_by'))
        for key, group in groupby(info, itemgetter('offered_by')):
            department_list.remove(key)
            product_info = dict()
            product_info['product_name'] = key
            product_info['sub_series'] = []
            series_info = list(group)
            # series_info.sort(key=itemgetter('product_series'), reverse=True)
            product_series_list = []
            for serie in series_info:
                product_series = serie.get('product_series')
                if not product_series:
                    product_series = 'UNKNOWN'
                if product_series not in product_series_list:
                    product_series_list.append(product_series)
                    temp = dict()
                    temp['product_series'] = product_series
                    product_info['sub_series'].append(temp)
            # 每一个offered_by都确保有UNKNOWN
            print(product_series_list)
            if 'UNKNOWN' not in product_series_list:
                UNKNOWN_info = dict()
                UNKNOWN_info.update(product_series='UNKNOWN')
                product_info['sub_series'].append(UNKNOWN_info)
            res.append(product_info)

        if department_list:
            for last_department in department_list:
                last_department_info = dict()
                last_department_info['product_name'] = last_department
                UNKNOWN_info = dict()
                UNKNOWN_info.update(product_series='UNKNOWN')
                last_department_info['sub_series'] = [UNKNOWN_info]
                res.append(last_department_info)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": res})


class ProductUuid(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, env, uuid):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        else:
            db_url = Sidus_Dev_Database

        conn, cursor = SQLHepler.sql_multi_open(db_url)
        data = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Product_UUID, args=uuid, cursor=cursor)
        SQLHepler.close(conn=conn, cursor=cursor)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})


class ManageProduct(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, env, offered, series):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        else:
            db_url = Sidus_Dev_Database
        if offered == 'ALL':
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_All_Product, db_dict=db_url)
        elif offered != 'ALL' and series == 'ALL':
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_Product, args=offered, db_dict=db_url)
        else:
            hardware_p_info = SQLHepler.fetch_all(SQL_Hardware_Product_offered_series, args=(offered, series),
                                                  db_dict=db_url)
        # 获取参与人员列表信息
        info = []
        for data in hardware_p_info:
            uuid = data.get('uuid')
            instance = ProdPartner.objects.filter(pro_uuid=uuid)
            creator = None
            partner = []
            if instance:
                serializer = ProdPartnerSerializer(instance=instance, many=True)
                partner = serializer.data[0].get('pro_user')
                creator = serializer.data[0].get('pro_create')
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

    def post(self, request, env, offered, series):
        if offered == 'add' and series == 'firmware_product':
            data = request.data.copy()
            uuid_ascii_code = data.get('uuid_ascii_code')
            user = request.user
            # 产品新建，默认状态为0
            data.update(product_status=0)
            # pro调用接口，dev SQL 写入数据
            if env == 'pro':
                sidus_token = user.sidus_token
                header = {
                    'Token-Data': sidus_token
                }
                res = requests.post(Sidus_Pro_FirmWareProductUrl, data=data,
                                    headers=header).json()
                return Response({"status": res.get('status'), "msg": res.get('msg')})
            elif env == 'dev':
                if not uuid_ascii_code:
                    return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
                db_url = Sidus_Dev_Database
                conn, cursor = SQLHepler.sql_multi_open(db_url)
                # 判断是否已经存在
                res_info = SQLHepler.sql_multi_fetch_one(SQL_Firware_Product_Count, args=uuid_ascii_code,
                                                         cursor=cursor)
                if int(res_info.get('count')) >= 1:
                    return Response({"status": RET.PORDUCTEXIST, "msg": uuid_ascii_code + ' Already Existed'})
                # 数据处理
                data.update(product_updated_admin_name=user.first_name + " " + user.last_name)
                try:
                    SQLHepler.sql_multi_execute(SQL_Insert_Firware_Product, args=data, cursor=cursor)
                    SQLHepler.close(conn=conn, cursor=cursor)
                except Exception as e:
                    return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            else:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def put(self, request, env, offered, series):
        if offered == 'update':
            data = request.data.copy()
            id = series
            user = request.user
            # pro dev SQL 更新数据
            if env == 'pro':
                db_url = Sidus_Pro_Database
            elif env == 'dev':
                db_url = Sidus_Dev_Database
            else:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

            conn, cursor = SQLHepler.sql_multi_open(db_url)
            # 判断是否已经存在
            res_info = SQLHepler.sql_multi_fetch_one(SQL_Firware_Product_Count_By_Id, args=id,
                                                     cursor=cursor)
            if int(res_info.get('count')) < 1:
                return Response({"status": RET.PORDUCTNOTEXIST, "msg": 'Product_id:' + id + ' Not Exist'})
            # 数据处理
            data.update(product_updated_admin_name=user.first_name + " " + user.last_name, id=id)

            try:
                SQLHepler.sql_multi_execute(SQL_Updatet_Firware_Product, args=data, cursor=cursor)
                SQLHepler.close(conn=conn, cursor=cursor)
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": e})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def delete(self, request, env, offered, series):
        if offered == 'delete':
            uuid_ascii_code = series
            if env == 'pro':
                db_url = Sidus_Pro_Database
            elif env == 'dev':
                db_url = Sidus_Dev_Database
            else:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

            conn, cursor = SQLHepler.sql_multi_open(db_url)
            try:
                # 判断是否已经存在
                res_info = SQLHepler.sql_multi_fetch_one(SQL_Firware_Product_Count, args=uuid_ascii_code,
                                                         cursor=cursor)
                if int(res_info.get('count')) < 1:
                    return Response({"status": RET.PORDUCTNOTEXIST, "msg": uuid_ascii_code + ' Not Exist'})
                # 删除制定固件信息
                SQLHepler.sql_multi_execute(SQL_Delete_Firware_UUID, args=uuid_ascii_code, cursor=cursor)
                SQLHepler.sql_multi_execute(SQL_Delete_Firware_Product, args=uuid_ascii_code, cursor=cursor)
                SQLHepler.close(conn=conn, cursor=cursor)
                # 删除项目的创建人员以及协作人员
                ProdPartner.objects.filter(pro_uuid=uuid_ascii_code).delete()
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


class CreatedManageProduct(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, env, offered, series):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        else:
            db_url = Sidus_Dev_Database
        if offered == 'ALL':
            hardware_p_info = SQLHepler.fetch_all(SQL_Created_Hardware_All_Product, db_dict=db_url)
        elif offered != 'ALL' and series == 'ALL':
            hardware_p_info = SQLHepler.fetch_all(SQL_Created_Hardware_Product, args=offered, db_dict=db_url)
        else:
            hardware_p_info = SQLHepler.fetch_all(SQL_Created_Hardware_Product_offered_series, args=(offered, series),
                                                  db_dict=db_url)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": hardware_p_info})

    def delete(self, request, env, offered, series):
        if offered == 'delete':
            uuid_ascii_code = series
            if env == 'pro':
                db_url = Sidus_Pro_Database
            elif env == 'dev':
                db_url = Sidus_Dev_Database
            else:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

            conn, cursor = SQLHepler.sql_multi_open(db_url)
            try:
                # 删除制定固件信息,并将product_status=0 标记为未使用
                SQLHepler.sql_multi_execute(SQL_Delete_Firware_UUID, args=uuid_ascii_code, cursor=cursor)
                SQLHepler.sql_multi_execute(SQL_Status_Firware_Product, args=uuid_ascii_code, cursor=cursor)
                SQLHepler.close(conn=conn, cursor=cursor)
                # 删除项目的创建人员以及协作人员
                ProdPartner.objects.filter(pro_uuid=uuid_ascii_code).delete()
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def put(self, request, env, offered, series):
        if offered == 'update':
            id = series
            if env == 'pro':
                db_url = Sidus_Pro_Database
            elif env == 'dev':
                db_url = Sidus_Dev_Database
            else:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
            try:
                # 隐藏指定固件信息
                SQLHepler.sql_execute(SQL_Display_Firware_Product, args=id, db_dict=db_url)
                return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


class ManageHardWareFirmware(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, env, uuid):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        conn, cursor = SQLHepler.sql_multi_open(db_url)
        uuid = uuid

        firmware_info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Firmware, args=uuid,
                                                      cursor=cursor)
        data = {}
        ctr = []
        dr = []
        ble = []
        ble_hardware_list = []
        for info in firmware_info:
            if info.get('firmware_type') == 'Ctr':
                res = self.get_firmware(info, uuid, cursor=cursor)
                ctr.append(res)
            elif info.get('firmware_type') == 'Dr':
                res = self.get_firmware(info, uuid, cursor=cursor)
                dr.append(res)
            elif info.get('firmware_type') == 'Ble':
                ble_hardware_version = info.get('hardware_version')
                ble_hardware_list.append(ble_hardware_version)
                res = self.get_firmware(info, uuid, cursor=cursor)
                ble.append(res)

        ble_hardware_versions = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Ble_Firmware,
                                                              args=uuid, cursor=cursor)
        normal_ble_versions = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Ble_Firmware,
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
                    normal_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_Blue_Version,
                                                                args=normal_version, cursor=cursor)
                    if normal_info:
                        normal_info.update(normal_exist=1, history=[])
                        ble.append(normal_info)

        SQLHepler.close(conn=conn, cursor=cursor)
        # 构建输出数据结构
        data['ctr'] = ctr
        data['dr'] = dr
        data['ble'] = ble
        with open("./test.txt",'w') as f:
            f.write(str(data))
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})

    @staticmethod
    def get_firmware(info, uuid, cursor):
        h_version = info.get('hardware_version')
        h_type = info.get('firmware_type')
        history_info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Firmware,
                                                     args=(uuid, h_version, h_type),
                                                     cursor=cursor)
        infos = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Firmware_Blue_Client, cursor=cursor)
        if infos:
            info.update(normal_exist=1)
        else:
            info.update(normal_exist=0)
        info.update(history=history_info)
        return info

    def put(self, request, env, uuid):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        firmware_id = uuid
        try:
            SQLHepler.sql_execute(SQL_Display_Firware, args=firmware_id, db_dict=db_url)
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def delete(self, request, env, uuid):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        firmware_id = uuid
        conn, cursor = SQLHepler.sql_multi_open(db_url)
        try:
            # 先获取信息,再执行删除
            firmware_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, args=firmware_id,
                                                          cursor=cursor)
            if not firmware_info:
                return Response({"status": RET.FIRMWARNOTEXIST, "msg": Info_Map[RET.FIRMWARNOTEXIST]})

            uuid_ascii_code = firmware_info.get('uuid_ascii_code')
            firmware_type = firmware_info.get('firmware_type')
            hardware_version = firmware_info.get('hardware_version')
            firmware_version = firmware_info.get('firmware_version')
            # 如果是线上服,需要将测试服的此固件状态置为0
            if env == 'pro':
                dev_conn, dev_cursor = SQLHepler.sql_multi_open(Sidus_Dev_Database)
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Disable_Firmware_Status,
                                            args=(
                                                uuid_ascii_code, firmware_type, hardware_version, firmware_version),
                                            cursor=dev_cursor)
                SQLHepler.close(conn=dev_conn, cursor=dev_cursor)
            SQLHepler.sql_multi_execute(SQL_Delete_Firware_Hardware_Version,
                                        args=(uuid_ascii_code, firmware_type, hardware_version), cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})


class ManagePublish(APIView):
    """发布固件信息到正式"""
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        try:
            info = SQLHepler.fetch_one(SQL_Hardware_Firmware_ID, args=id, db_dict=Sidus_Dev_Database)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        # 更新到线上
        dev_conn, dev_cursor = SQLHepler.sql_multi_open(Sidus_Dev_Database)
        pro_conn, pro_cursor = SQLHepler.sql_multi_open(Sidus_Pro_Database)
        try:
            uuid_ascii_code = info.get('uuid_ascii_code')
            firmware_type = info.get('firmware_type')
            hardware_version = info.get('hardware_version')
            firmware_version = info.get('firmware_version')
            # 检测正式服是否有此固件
            firmware_res = SQLHepler.sql_multi_fetch_one(SQL_Update_Hardware_Firmware_Exist,
                                                         (uuid_ascii_code, firmware_type, hardware_version,
                                                          firmware_version),
                                                         cursor=pro_cursor)

            # 检测正式服是否有此产品
            product_res = SQLHepler.sql_multi_fetch_one(SQL_Firware_Product_Count, args=uuid_ascii_code,
                                                        cursor=pro_cursor)
            if int(product_res.get('count')) < 1:
                # 从测试服获取此产品信息
                product_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Product_INFO_BY_UUID, args=uuid_ascii_code,
                                                             cursor=dev_cursor)
                del product_info['id']
                # 新增此产品
                SQLHepler.sql_multi_execute(SQL_Insert_Firware_Product, args=product_info, cursor=pro_cursor)

            # 更新测试服当前的数据的status=1
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_Status, id, cursor=dev_cursor)
            info.update(firmware_status=1, firmware_environment=1)
            # 判断
            if int(firmware_res.get('count')) >= 1:
                info.update(id=firmware_res.get('id'))
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware, args=info,
                                            cursor=pro_cursor)
            else:
                # PRO使其他相同hardware_version失效
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_available,
                                            (uuid_ascii_code, firmware_type, hardware_version), cursor=pro_cursor)
                # 插入数据到PRO
                SQLHepler.sql_multi_execute(SQL_Insert_Hardware_Firmware, info, cursor=pro_cursor)

            SQLHepler.close(conn=dev_conn, cursor=dev_cursor)
            SQLHepler.close(conn=pro_conn, cursor=pro_cursor)
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": str(e)})


class ManagePublishNormalBlue(APIView):
    """发布通用蓝牙信息到正式服"""
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        dev_conn, dev_cursor = SQLHepler.sql_multi_open(Sidus_Dev_Database)
        pro_conn, pro_cursor = SQLHepler.sql_multi_open(Sidus_Pro_Database)

        try:
            info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, args=id, cursor=dev_cursor)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        # 更新到线上
        try:
            # 更新测试服当前的数据的status=1
            SQLHepler.sql_multi_fetch_one(SQL_Update_Hardware_Firmware_Status, id, cursor=dev_cursor)
            info.update(firmware_status=1)
            # 更新pro所有的通用蓝牙信息
            # 检测正式服是否有此固件
            firmware_res = SQLHepler.sql_multi_fetch_one(SQL_Update_Hardware_Firmware_Exist,
                                                         ('normal', 'Ble', info.get('hardware_version'),
                                                          info.get('firmware_version')),
                                                         cursor=pro_cursor)
            if int(firmware_res.get('count')) >= 1:
                SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_Normal_Ble, info, cursor=pro_cursor)
            else:
                # 新增此产品
                SQLHepler.sql_multi_execute(SQL_Insert_Hardware_Firmware, args=info, cursor=pro_cursor)

            SQLHepler.close(conn=dev_conn, cursor=dev_cursor)
            SQLHepler.close(conn=pro_conn, cursor=pro_cursor)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class ManageAvailableNormalBlue(APIView):
    """测试服启用通用蓝牙"""
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        user = request.user
        db_url = Sidus_Dev_Database
        try:
            conn, cursor = SQLHepler.sql_multi_open(db_url)
            info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, args=id, cursor=cursor)
            hardware_version = info.get('hardware_version')
            # 更新当前hardware版本的蓝牙
            # SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_Normal_Ble, info, cursor=cursor)
            # 将当前硬件版本的其他固件不激活
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_normal_available, hardware_version, cursor=cursor)
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_able, args=id, cursor=cursor)

            SQLHepler.close(conn=conn, cursor=cursor)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class ManageBlueView(APIView):
    """处理通用蓝牙"""
    permission_classes = [IsAdminUser]

    def get(self, request, env, id):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        if id == 'ALL':
            conn, cursor = SQLHepler.sql_multi_open(db_url)

            infos = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Firmware_Blue, cursor=cursor)
            result = []
            for info in infos:
                hardware_version = info.get('hardware_version')
                history_info = SQLHepler.sql_multi_fetch_all(SQL_Hardware_Unavail_Firmware,
                                                             args=('normal', hardware_version, 'Ble'), cursor=cursor)
                info.update(history=history_info)
                result.append(info)
            SQLHepler.close(conn=conn, cursor=cursor)
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK], 'data': result})
        else:
            Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def post(self, request, env, id):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        conn, cursor = SQLHepler.sql_multi_open(db_url)
        if id == "add":
            user = request.user
            data = request.data.copy()
            try:
                self.insert_data(cursor, user, **data)
                SQLHepler.close(conn=conn, cursor=cursor)
            except ValueError as e:
                return Response({"status": RET.PARAMERR, "msg": str(e)})
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": str(e)})
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        else:
            Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    def put(self, request, env, id):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        conn, cursor = SQLHepler.sql_multi_open(db_url)

        data = request.data.copy()
        user = request.user
        data.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, id=id)
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
                return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        # 对应的信息，更新到所有的使用通用蓝牙的固件
        # self.normalble_update(cursor, id)
        SQLHepler.close(conn=conn, cursor=cursor)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    # @staticmethod
    # def normalble_update(cursor, id):
    #     info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, id, cursor=cursor)
    #     # 更新所有的通用蓝牙信息
    #     SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_Normal_Ble, info, cursor=cursor)

    def delete(self, request, env, id):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        firmware_id = id
        conn, cursor = SQLHepler.sql_multi_open(db_url)
        try:
            # 如果删除的线上,更新测试对应的数据
            if env == 'pro':
                # 先获取线上的数据
                firmware_info = SQLHepler.sql_multi_fetch_one(SQL_Hardware_Firmware_ID, args=firmware_id,
                                                              cursor=cursor)
                if firmware_info:
                    uuid_ascii_code = firmware_info.get('uuid_ascii_code')
                    if uuid_ascii_code == 'normal':
                        firmware_type = firmware_info.get('firmware_type')
                        hardware_version = firmware_info.get('hardware_version')
                        firmware_version = firmware_info.get('firmware_version')
                        dev_conn, dev_cursor = SQLHepler.sql_multi_open(Sidus_Dev_Database)
                        SQLHepler.sql_multi_execute(SQL_Update_Hardware_Disable_Firmware_Status,
                                                    args=(uuid_ascii_code, firmware_type, hardware_version,
                                                          firmware_version), cursor=dev_cursor)
                        SQLHepler.close(conn=dev_conn, cursor=dev_cursor)

            SQLHepler.sql_multi_execute(SQL_Delete_Firware_ID, args=firmware_id, cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

    @staticmethod
    def insert_data(cursor, user, **kwargs):
        uuid_ascii_code = 'normal'
        firmware_type = 'Ble'
        hardware_version = kwargs.get('hardware_version')
        firmware_version = kwargs.get('firmware_version')
        # 查询是否已经有存在
        res = SQLHepler.sql_multi_fetch_one(SQL_Update_Hardware_Firmware_Exist,
                                            (uuid_ascii_code, firmware_type, hardware_version, firmware_version),
                                            cursor=cursor)
        if int(res.get('count')) >= 1:
            firmware_id = res.get('id')
            kwargs.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, id=firmware_id)
            firmware_file = kwargs.get('firmware_url')
            if firmware_file:
                try:
                    SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_with_file, kwargs, cursor=cursor)
                except Exception as e:
                    return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
            else:
                try:
                    SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_without_file, kwargs, cursor=cursor)
                except Exception as e:
                    return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        else:
            # 将当前硬件版本的其他固件不激活
            SQLHepler.sql_multi_execute(SQL_Update_Hardware_Firmware_normal_available, hardware_version, cursor=cursor)

            kwargs.update(firmware_updated_admin_name=user.first_name + " " + user.last_name, uuid_ascii_code='normal',
                          firmware_normal=1, firmware_type='Ble', firmware_status=0)
            SQLHepler.sql_multi_execute(SQL_Insert_Hardware_Firmware, kwargs, cursor=cursor)


class ProductSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, env, info):
        if env == 'pro':
            db_url = Sidus_Pro_Database
        elif env == 'dev':
            db_url = Sidus_Dev_Database
        else:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        res = SQLHepler.fetch_all(SQL_Hardware_Product_Search.format(info, info, info, info),
                                  db_dict=db_url)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": res})


class UserSearchView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get(self, request, info):
        infos = SQLHepler.fetch_all(SQL_Hardware_User_Search.format(info),
                                    db_dict=Local_Database_Iot)
        data = []
        for info in infos:
            id = info.get('id')
            instance = User.objects.filter(id=id)
            serializer = self.get_serializer(instance, many=True)
            data.extend(serializer.data)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})


class DepartmentSearchView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ManageDepartmentSerializer

    def get(self, request, info):
        infos = SQLHepler.fetch_all(SQL_Hardware_Department_Search.format(info),
                                    db_dict=Local_Database_Iot)
        data = []
        for info in infos:
            id = info.get('id')
            instance = Department.objects.filter(id=id)
            serializer = self.get_serializer(instance, many=True)
            data.extend(serializer.data)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": data})


from user.views import UserRequetView


class RequestView(UserRequetView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        instance = self.get_queryset().filter(status=0)
        serializer = self.get_serializer(instance, many=True)

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})

    def put(self, request):
        # 拒绝申请
        info = request.data.copy()
        request_id = info.get('id')
        # 避免恶意上传数据
        if info.get('status'):
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        instance = self.get_queryset().filter(id=request_id).first()
        if not instance:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        # status=2，拒绝
        info.update(status=2)
        serializer = self.get_serializer(data=info, instance=instance)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": str(e)})
        serializer.save()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class RequestPassView(UpdateUserView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        info = request.data
        # 避免恶意上传数据
        if info.get('status'):
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})
        # 更新请求状态,status=1,通过
        RequestInfo.objects.filter(user=pk).update(status=1)
        roles = info.get('roles')
        user = User.objects.filter(id=pk).first()
        if 1 in roles:
            user.is_staff = 1
            user.save()
        serializer = self.get_serializer(data=info, instance=self.get_object())
        serializer.is_valid(raise_exception=True)

        # 保存改用户数据到测试服
        try:
            pro_db_url = Sidus_Pro_Database
            dev_db_url = Sidus_Dev_Database
            # 正式服操作
            pro_conn, pro_cursor = SQLHepler.sql_multi_open(pro_db_url)
            email = user.username
            pro_user_info = SQLHepler.sql_multi_fetch_one(SQL_User_Get, args=email, cursor=pro_cursor)
            SQLHepler.close(conn=pro_conn, cursor=pro_cursor)
            # 测试服操作
            dev_conn, dev_cursor = SQLHepler.sql_multi_open(dev_db_url)
            dev_user_info = SQLHepler.sql_multi_fetch_one(SQL_User_Get, args=email, cursor=dev_cursor)
            if not dev_user_info:

                SQLHepler.sql_multi_execute(SQL_User_Insert, args=pro_user_info, cursor=dev_cursor)
            SQLHepler.close(conn=dev_conn, cursor=dev_cursor)
        except Exception as e:
            Response({"status": RET.PARAMERR, "msg": str(e)})
        serializer.save()
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})


class RequestDenyView(UpdateUserView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        # 拒绝申请

        # 更新请求状态,status=2,拒绝
        RequestInfo.objects.filter(user=pk).update(status=2)

        # serializer = self.get_serializer(data=info, instance=self.get_object())
        # serializer.is_valid(raise_exception=True)
        # serializer.save()

        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class PartnerView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProdSerializer
    queryset = ProdPartner.objects.all()

    def post(self, request):
        info = request.data.copy()
        uuid = info.get('pro_uuid')
        user_ids = info.get('pro_user')
        instance = self.queryset.filter(pro_uuid=uuid).first()
        if not instance:
            try:
                info.update(pro_create=None)
                print(info)
                serializer = self.get_serializer(data=info)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except Exception as e:
                return Response({"status": RET.PARAMERR, "msg": str(e)})
            return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
        # 获取所有的id
        for user_id in user_ids:
            instance.pro_user.add(user_id)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def delete(self, request):
        info = request.data
        user_ids = info.get('pro_user')
        uuid = info.get('pro_uuid')
        instance = ProdPartner.objects.filter(pro_uuid=uuid).first()
        for user_id in user_ids:
            instance.pro_user.remove(user_id)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})


class ClientProductList(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FirmwareProdSerializer
    queryset = FirmwareProduct.objects.all()

    def get(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK], "data": serializer.data})

    def delete(self, request):
        prd_id = request.data.get('id')
        instance = self.get_queryset().filter(id=prd_id)
        if instance:
            instance.delete()
        else:
            return Response({"status": RET.PARAMERR, "msg": '当前产品不存在'})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})

    def post(self, request):
        data = request.data.copy()
        uuid_ascii_code = data.get('uuid_ascii_code')
        client_product_id = data.get('id')
        if not uuid_ascii_code:
            return Response({"status": RET.PARAMERR, "msg": Info_Map[RET.PARAMERR]})

        db_url = Sidus_Dev_Database
        conn, cursor = SQLHepler.sql_multi_open(db_url)

        res_info = SQLHepler.sql_multi_fetch_one(SQL_Firware_Product_Count, args=uuid_ascii_code,
                                                 cursor=cursor)
        if int(res_info.get('count')) >= 1:
            return Response({"status": RET.PORDUCTEXIST, "msg": uuid_ascii_code + ' Already Existed'})

            # 数据处理
        client_product = FirmwareProduct.objects.filter(id=client_product_id).first()
        if client_product:
            client_product.delete()
        del data['id']
        user = request.user
        data.update(product_updated_admin_name=user.first_name + " " + user.last_name, product_status=0)
        try:
            SQLHepler.sql_multi_execute(SQL_Insert_Firware_Product, args=data, cursor=cursor)
            SQLHepler.close(conn=conn, cursor=cursor)
        except Exception as e:
            return Response({"status": RET.PARAMERR, "msg": str(e)})
        return Response({"status": RET.OK, "msg": Info_Map[RET.OK]})
