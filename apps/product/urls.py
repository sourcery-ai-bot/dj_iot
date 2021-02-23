from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hardware/(?P<offered>[\u4e00-\u9fa5_a-zA-Z0-9\s]+)/(?P<series>[\w\s]+)/$', views.HardWareProduct.as_view()),
    url(r'^hardware_list/$', views.ProductList.as_view()),
    url(r'^uuid/(?P<uuid>\w+)/$', views.ProductUuid.as_view()),
    url(r'^firmware/(?P<uuid>[\x00-\x7f]+)/$', views.HardWareFirmware.as_view()),
    url(r'^upload/firmware/$', views.UploadFile.as_view()),
    url(r'^search/(?P<info>\w+)/$', views.ClientSearchView.as_view()),
    url(r'^operate_firmware/(?P<id>\w+)/$', views.OperateFirmwareView.as_view()),
    url(r'^firmware_backble/(?P<uuid>[\x00-\x7f]+)/$', views.BackNormalBleView.as_view()),
    url(r'^partner/$', views.ClientPaternerView.as_view()),
    url(r'^client_add/$', views.ClientFirmwareProductView.as_view()),
    url(r'^users/$', views.ClientUser.as_view()),
    url(r'^check_normal/$', views.CheckNormalExistedView.as_view())
]
