import os

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Max, Min
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, HttpResponse
from django.http.response import JsonResponse
from django.contrib import auth
from django.db import transaction
from Blog.models import UserInfo
from Blog.utils.Myforms import UserForm
from .utils.geetest import GeetestLib
from Blog import models
from Blog_Demo import settings

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# Create your views here.
def login(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail", 'msg': 'valid code error!'}
        # 如果验证码通过则效验密码
        if result:
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user==当前登陆对象
                result['user'] = user.username
                result['url'] = request.GET.get('next')
            else:
                result['msg'] = 'username or password error!'
        return JsonResponse(result)
    return render(request, 'login.html')


def get_validCode_img(request):
    '''
    基于PIL模块动态生成响应验证码图片
    :param request:
    :return:
    '''

    from Blog.utils.vaild_Code import get_vaild_code_img
    data = get_vaild_code_img(request)
    return HttpResponse(data)


def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {'article_list': article_list})


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def ajax_validate(request):
    return None


def register(request):
    if request.is_ajax():
        form = UserForm(request.POST)
        response = {'user': None, 'msg': None}
        if form.is_valid():
            response['user'] = form.cleaned_data.get('user')

            # 生成一条用户记录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar = request.FILES.get('avatar')
            extra = {}
            if avatar:  # 如果没有头像就不传
                extra['avatar'] = avatar
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            print(form.cleaned_data)
            print(form.error_class)
            response['msg'] = form.errors
        return JsonResponse(response)
    form = UserForm()
    return render(request, 'register.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def home_site(request, username, **kwargs):
    '''
    个人站点视图函数
    :param request:
    :param username:
    :param kwargs:
    :return:
    '''

    print(kwargs)
    user = UserInfo.objects.filter(username=username).first()
    # 判断用户是否存在
    if not user:
        return render(request, 'not_found.html')
    # 查询当前站点对象
    blog = user.blog
    # 当前用户或者当前站点对应的所有文章
    article_list = models.Article.objects.filter(user=user)
    # 基于对象查询
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category__title=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    # 基于__
    # article_list = models.Article.objects.filter(user=user).first()
    # 查询每一个分类名称以及对应的文章数
    # cate_list = models.Category.objects.values('pk').annotate(c=Count("article__title")).values('title', 'c')
    # 查询当前站点的每一个分类名称以及对应的文章数
    # cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list
    # (
    #     "title", "c")
    # 查询当前站点的每一个标签以及对应的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article')).values_list('title', 'c'
    # )
    # 查询当前站点每一个年月的名称以及对应的文章数。
    # ret=models.Article.objects.extra(select={'is_recent':"create_time>'2018-09-09'"})
    # date_list = models.Article.objects.filter(user=user).extra(
    #     select={'y_m_date': "strftime('%%Y-%%m',create_time)"}).values_list('y_m_date').annotate(
    #     c=Count('nid')).values_list(
    #     'y_m_date', 'c')
    # date_list = models.Article.objects.filter(user=user).annotate(mouth=TruncMonth('create_time')).values_list(
    #     'mouth').annotate(
    #     c=Count('nid')).values_list('mouth', 'c')
    return render(request, 'home_site.html', locals())


def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=article_id).get()
    comment_list = models.Comment.objects.filter(article_id=article_id)
    return render(request, 'article_detail.html', locals())


import json
from django.db.models import F


def digg(request):
    if request.is_ajax():
        print(request.POST)
        article_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))
        user_id = request.user.pk
        obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        response = {"state": True, "handled": None}
        if not obj:
            ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
            queryset = models.Article.objects.filter(pk=article_id)
            if is_up:
                queryset.update(up_count=F('up_count') + 1)
            else:
                queryset.update(down_count=F("down_count") + 1)
        else:
            response["state"] = False
            response["handled"] = obj.is_up

        return JsonResponse(response)
    return render(request, 'not_found.html')


def comment(request):
    print(request.POST)
    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    pid = request.POST.get('pid')
    # 事务操作，同进同退
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=request.user.pk, article_id=article_id, content=content,
                                                    parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)
    response = {}

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content
    response["parent_comment_id"] = comment_obj.parent_comment_id

    article_obj = models.Article.objects.filter(article_id=article_id).first()
    # 发送邮件
    from django.core.mail import send_mail
    from Blog_Demo import settings

    import threading
    t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论内容" % article_obj.title,
                                                 content,
                                                 settings.EMAIL_HOST_USER,
                                                 [article_obj.user.email]))
    t.start()
    return JsonResponse(response)


def get_comment_tree(request):
    print(request.GET)
    article_id = request.GET.get('article_id')
    ret = list(models.Comment.objects.filter(article_id=article_id).order_by('pk').values('pk', 'content',
                                                                                          'parent_comment_id'))
    return JsonResponse(ret, safe=False)


@login_required
def cn_backend(request):
    article_list = models.Article.objects.filter(user=request.user)
    return render(request, "backend/backend.html", locals())


@login_required
def cn_backend_add(request):
    if request.is_ajax():
        print(request.POST)
        title = request.POST.get('title')
        content = request.POST.get('content')
        models.Article.objects.create(user=request.user, title=title, content=content)
        ret = {'msg': True}
        return JsonResponse(ret)
    return render(request, "backend/add.html", locals())


def upload(request):
    print(request.FILES)
    img = request.FILES.get('upload_img')
    path = os.path.join(settings.MEDIA_ROOT, 'add_article_img', img.name)
    with open(path, 'wb') as f:
        for line in img:
            f.write(line)

    return HttpResponse('OK')
