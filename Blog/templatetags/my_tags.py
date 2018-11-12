from django import template
from django.db.models import Count

from Blog import models

register = template.Library()


@register.simple_tag()
def multi_tag(x, y):
    return x * y


@register.inclusion_tag('classification.html')
def get_classification_style(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article')).values_list('title', 'c')
    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_m_date': "strftime('%%Y-%%m',create_time)"}).values_list('y_m_date').annotate(
        c=Count('nid')).values_list(
        'y_m_date', 'c')
    return {'blog': blog, 'cate_list': cate_list, 'tag_list': tag_list, 'date_list': date_list, 'username': username}
