import random


def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_vaild_code_img(request):
    # pip install pillow
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    import string

    img = Image.new('RGB', (277, 40), color=get_random_color())  # 实例化Img对象
    draw = ImageDraw.Draw(img)  # 创建一个画布
    kumo = ImageFont.truetype('static/font/kumo.ttf', size=28)  # 读取字体
    valid_code_str = ''
    for i in range(5):
        # 生成随机字符串 方法1
        # random_num = str(random.randint(0, 9))
        # random_low_alpha = chr(random.randint(95, 122))
        # random_upper_alpha = chr(random.randint(65, 90))
        # random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        # 生成随机字符串 方法2
        random_char = ''.join(random.sample(string.ascii_letters + string.digits, 1))
        # 使用字体写入文本
        draw.text((i * 50 + 20, 5), random_char, get_random_color(), font=kumo)
        # 保存验证码字符串
        valid_code_str += random_char
    # 补充噪点噪线
    # width = 270
    # height = 40
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, y1, x2, y2), fill=get_random_color())
    #
    # for i in range(100):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    f = BytesIO()
    img.save(f, 'png')  # 把图片放到内存中
    data = f.getvalue()  # 把图片读取返回给客户端
    request.session['valid_code_str'] = valid_code_str  # 保存用户验证码
    '''
    1.生成随机字符串
    2.COOKIE {'sessionid':随机字符串}
    3.django-session
    session-key             session-data
     随机验证码                  {"valid_code_str":valid_code_str}
    '''
    return data
