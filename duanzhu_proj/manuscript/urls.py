from django.urls import path
from .views import catalogue_data, zitou_detail, zstag_detail, index, search, yinyitong, zhishimulu_data, xiangxing,zhishi,huiyi,xingsheng,zhuanzhu,jiajie,tongzi,xingfeizi,huxun,zhiyan,lianmianci,yinshen,benyi,gujinyi,gouyi

urlpatterns = [
    path('', index, name='index'),
    path('catalogue/', catalogue_data, name='catalogue'),
    path('zsTag/<uuid:zitou_id>/tag/<str:tag>/', zstag_detail, name='zstag_detail'),
    path('zitou/<uuid:zitou_id>/', zitou_detail, name='zitou_detail'),
    path('search/', search, name='search'),
    path('zhishimulu/', zhishimulu_data, name='zhishimulu'),
    path('yinyitong/', yinyitong, name='yinyitong'),
    path('xiangxing/', xiangxing, name='xiangxing'),
    path('zhishi/', zhishi, name='zhishi'),
    path('huiyi/', huiyi, name='huiyi'),
    path('xingsheng/', xingsheng, name='xingsheng'),
    path('zhuanzhu/', zhuanzhu, name='zhuanzhu'),
    path('jiajie/', jiajie, name='jiajie'),
    path('tongzi/', tongzi, name='tongzi'),
    path('xingfeizi/', xingfeizi, name='xingfeizi'),

    path('huxun/', huxun, name='huxun'),
    path('zhiyan/', zhiyan, name='zhiyan'),
    path('lianmianci/', lianmianci, name='lianmianci'),
    path('yinshen/', yinshen, name='yinshen'),
    path('benyi/', benyi, name='benyi'),
    path('gujinyi/', gujinyi, name='gujinyi'),
    path('gouyi/', gouyi, name='gouyi'),
]
