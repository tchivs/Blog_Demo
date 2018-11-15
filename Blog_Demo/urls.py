"""Blog_Demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from Blog import views
from django.conf.urls import url
from django.views.static import serve
from Blog_Demo import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('index/', views.index),
    # 后台管理url
    re_path('cn_backend$',views.cn_backend),
    re_path('cn_backend/add$',views.cn_backend_add),
    # 点赞
    path('digg/', views.digg),
    # 评论
    path('comment/', views.comment),
    # 获取评论树相关数据
    path('get_comment_tree/', views.get_comment_tree),
    path('ajax_validate/', views.ajax_validate),
    path('get_validCode_img/', views.get_validCode_img),
    url(r'^pc-geetest/register', views.pcgetcaptcha, name='pcgetcaptcha'),
    re_path(r'^$', views.index),
    # media配置
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # 个人站点URL
    re_path(r'^(?P<username>\w+)$', views.home_site),
    re_path(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site)
]
