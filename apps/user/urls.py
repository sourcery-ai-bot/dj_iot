from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'login/$', views.UserLoginView.as_view()),
    url(r'userinfo/$', views.UserInfoView.as_view()),
    url(r'changeinfo/$', views.ChangeUserView.as_view()),
    url(r'email_register/$', views.UserRegEmailView.as_view()),
    url(r'register/$', views.UserRegisterView.as_view()),
    url(r'update_pwd/$', views.UserChangePWD.as_view()),
    url(r'pwd_verify/$', views.UserPWDEMAILView.as_view()),
    url(r'departments/$', views.UserDepartmentsView.as_view()),
    url(r'requests/$', views.UserRequetView.as_view()),
    url(r'email_login_code/$', views.EmailLoginView.as_view()),
    url(r'verify_regcode/$', views.VerifyRegInfo.as_view()),
    url(r'delete/(?P<email>[\w@.]+)/$', views.UserDel.as_view()),
    url(r'change_avatar/$', views.ChangeUserAvatar.as_view())
]
