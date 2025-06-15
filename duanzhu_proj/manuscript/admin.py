from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = '说文段注知识库项目后台管理'
admin.site.site_title = '说文段注知识库'

@admin.register(DuanZhu)
class DuanZhuAdmin(admin.ModelAdmin):
    list_display = ('duanzhu_bianhao', 'zitou', 'chongwen', 'zhengwen_zhushi', 'bushou', 'juan')  # Customize the admin list view
    search_fields = ('zitou', 'zhengwen_zhushi',)  # Enable search functionality
    list_filter = ('status','juan',)

@admin.register(SwDu)
class SwDuZhuAdmin(admin.ModelAdmin):
    list_display = ('du_bianhao', 'zitou', 'zhushi', 'duanzhu_bianhao')  # Customize the admin list view
    search_fields = ('zitou','du_bianhao', 'zitou', 'zhushi', 'duanzhu_bianhao')  # Enable search functionality

@admin.register(Xiesheng)
class XieshengAdmin(admin.ModelAdmin):
    list_display = ('xieshengzi', 'shengfu')  # Customize the admin list view
    search_fields = ('xieshengzi', 'shengfu',)

@admin.register(Guyunbu)
class GuyunbuAdmin(admin.ModelAdmin):
    list_display = ('duanzhu_bianhao', 'zitou', 'yunbu', 'yunlei')  # Customize the admin list view
    search_fields = ('zitou','duanzhu_bianhao', 'zitou', 'yunbu', 'yunlei')

@admin.register(Gouyi)
class GouyiAdmin(admin.ModelAdmin):
    list_display = ('duanzhu_bianhao', 'gouyi1', 'gouyi2', 'gouyi3','shengfugouyi')  # Customize the admin list view
    search_fields = ('duanzhu_bianhao','gouyi1', 'gouyi2', 'gouyi3','shengfugouyi',)

@admin.register(Gujinzi)
class GujinziAdmin(admin.ModelAdmin):
    list_display = ('duanzhu_bianhao', 'chuxian_zitou', 'miaoshu', 'guzi_id','jinzi_id')  # Customize the admin list view
    search_fields = ('duanzhu_bianhao','chuxian_zitou', 'miaoshu','guzi_id','jinzi_id')