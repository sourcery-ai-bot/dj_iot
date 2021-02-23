from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'^role/(?P<role>\w+)/$', views.RoleUserView.as_view()),
    url(r'^roles/$', views.RoleListView.as_view()),
    url(r'^department/(?P<department>\w+)/$', views.DepartmentListView.as_view()),
    url(r'^departments/$', views.DepartmentsView.as_view()),
    url(r'^update/user/(?P<pk>\w+)/$', views.UpdateUserView.as_view()),
    url(r'^product/(?P<env>\w+)/(?P<offered>[\w\s]+)/(?P<series>[\x00-\x7f\w\s]+)/$', views.ManageProduct.as_view()),
    url(r'^products/(?P<env>\w+)/$', views.ManageProductList.as_view()),
    url(r'^product/(?P<env>\w+)/(?P<uuid>[\x00-\x7f]+)/$', views.ProductUuid.as_view()),
    url(r'^products_created/(?P<env>\w+)/$', views.ManageProductListCreated.as_view()),
    url(r'^created/product/(?P<env>\w+)/(?P<offered>[\w\s]+)/(?P<series>[\w\s]+)/$',
        views.CreatedManageProduct.as_view()),
    url(r'^firmware/(?P<env>\w+)/(?P<uuid>[\x00-\x7f]+)/$', views.ManageHardWareFirmware.as_view()),
    url(r'^publish/(?P<id>\w+)/$', views.ManagePublish.as_view()),
    url(r'^p_search/(?P<env>\w+)/(?P<info>\w+)/$', views.ProductSearchView.as_view()),
    url(r'^d_search/(?P<info>\w+)/$', views.DepartmentSearchView.as_view()),
    url(r'^u_search/(?P<info>\w+)/$', views.UserSearchView.as_view()),
    url(r'^normal_ble/(?P<env>\w+)/(?P<id>\w+)/$', views.ManageBlueView.as_view()),
    url(r'^publish_normal_ble/(?P<id>\w+)/$', views.ManagePublishNormalBlue.as_view()),
    url(r'^available_normal_ble/(?P<id>\w+)/$', views.ManageAvailableNormalBlue.as_view()),
    url(r'^request_info/$', views.RequestView.as_view()),
    url(r'^request_pass/(?P<pk>\w+)/$', views.RequestPassView.as_view()),
    url(r'^request_deny/(?P<pk>\w+)/$', views.RequestDenyView.as_view()),
    url(r'^partner/$', views.PartnerView.as_view()),
    url(r'^client_product/$', views.ClientProductList.as_view())
]
