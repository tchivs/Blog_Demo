from django import forms
from django.forms import widgets
from Blog.models import UserInfo
from django.core.exceptions import ValidationError


class UserForm(forms.Form):
    w1 = widgets.TextInput(attrs={'class': 'form-control'})
    w2 = widgets.PasswordInput(attrs={'class': 'form-control'})
    w3 = widgets.EmailInput(attrs={'class': 'form-control'})

    user = forms.CharField(max_length=32, widget=w1, label='用户名', error_messages={'required': '该字段不能为空'})
    pwd = forms.CharField(max_length=32, widget=w2, label='密码',error_messages={'required': '该字段不能为空'})
    re_pwd = forms.CharField(max_length=32, widget=w2, label='确认密码', error_messages={'required': '该字段不能为空'})
    email = forms.EmailField(max_length=32, widget=w3, label='邮箱', error_messages={'required': '该字段不能为空'})

    def clean_user(self):
        val = self.cleaned_data.get('user')
        user = UserInfo.objects.filter(username=val).first()
        if not user:
            return val
        else:
            raise ValidationError('该用户已注册！')

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致')
        return self.cleaned_data