from rest_framework import serializers
from product.models import Product
from utils.sql_sentences import SQL_Hardware_Product_Series, SQL_Created_Hardware_Product_Series
from utils.request_sidus import SQLHepler
from utils.constants import Sidus_Dev_Database, Sidus_Pro_Database


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ('create_time', 'update_time')


