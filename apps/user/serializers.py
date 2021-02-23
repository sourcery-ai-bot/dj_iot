from rest_framework import serializers
from user.models import User, Department, Role, RequestInfo
from rest_framework_jwt.settings import api_settings
import re
from django.core.exceptions import ValidationError


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ('create_time', 'update_time')

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        user_list = data['users']
        user_info = []
        for user_id in user_list:
            info = {}
            user = User.objects.get(id=user_id)
            info['id'] = user.id
            info['first_name'] = user.first_name
            info['last_name'] = user.last_name
            info['email'] = user.email
            info['sidus_avatar'] = user.sidus_avatar
            user_info.append(info)
        data['users'] = user_info
        return data


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ('create_time', 'update_time')


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(many=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'department', 'roles', 'sidus_avatar', 'avatar_color')

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     roles_list = data['roles']
    #     r_name = []
    #     for role_id in roles_list:
    #         name = Role.objects.get(id=role_id).role_name
    #         r_name.append(name)
    #     data['roles'] = r_name
    #
    #     return data


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password', 'first_name', 'last_name', 'last_login', 'email', 'date_joined', 'email_active',
            'sidus_avatar', 'sidus_id', 'sidus_token', 'avatar_color')

    def create(self, validate_data):
        """创建用户"""
        user = super().create(validate_data)
        # 调用Django的认证系统加密密码
        user.set_password(validate_data["password"])
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('sidus_avatar', 'first_name', 'last_name')


class UpdateUserPWDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)

    def update(self, instance, validated_data):
        """创建用户"""
        user = super().update(instance, validated_data)
        # 加密密码
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate(self, attrs):
        # p = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$")
        p = re.compile(r"^[#?!-@$%^&*0-9A-Za-z]{6,16}$")
        if not p.match(attrs['password']):
            raise ValidationError(u"pasword format error")
        return attrs


class ManageUpdateUserSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), many=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = User
        fields = ('department', 'roles')


class ManageDepartmentSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Department
        exclude = ('create_time', 'update_time',)

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        user_list = data['users']
        user_info = []
        for user_id in user_list:
            info = {}
            user = User.objects.get(id=user_id)
            info['id'] = user.id
            info['first_name'] = user.first_name
            info['last_name'] = user.last_name
            info['email'] = user.email
            info['sidus_avatar'] = user.sidus_avatar
            user_info.append(info)
        data['users'] = user_info
        return data


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestInfo
        exclude = ('create_time', 'update_time')

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)

        user_id = data.get('user')
        user_info = UserSerializer(instance=User.objects.get(id=user_id)).data
        data['user'] = user_info
        return data
