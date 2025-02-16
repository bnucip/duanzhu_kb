from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = '说文段注知识库项目后台管理'
admin.site.site_title = '说文段注知识库'

@admin.register(DuanZhu)
class DuanZhuAdmin(admin.ModelAdmin):
    list_display = ('duanzhu_bianhao', 'zitou', 'chongwen', 'zhengwen_zhushi', 'bushou', 'juan')  # Customize the admin list view
    search_fields = ('zitou', 'zhengwen_zhushi',)  # Enable search functionality