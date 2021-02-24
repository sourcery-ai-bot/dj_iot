from rest_framework import serializers
from product.models import ProdPartner, FirmwareProduct
from user.serializers import UserSerializer
from user.models import User


class ProdPartnerSerializer(serializers.ModelSerializer):
    pro_user = UserSerializer(many=True)
    pro_uuid = serializers.CharField(write_only=True)
    pro_create = UserSerializer()

    class Meta:
        model = ProdPartner
        exclude = ('create_time', 'update_time', 'id')


class ProdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdPartner
        exclude = ('create_time', 'update_time')


class FirmwareProdSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmwareProduct
        exclude = ('create_time', 'update_time', 'uuid_ascii_code')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user_id = data.get('submit_user')
        user_info = UserSerializer(instance=User.objects.get(id=user_id)).data
        data['submit_user'] = user_info
        return data
