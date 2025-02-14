from django.urls import path
from .views import catalogue_data, zitou_detail, index, search

urlpatterns = [
    path('', index, name='index'),
    path('catalogue/', catalogue_data, name='catalogue'),
    path('zitou/<uuid:zitou_id>/', zitou_detail, name='zitou_detail'),
    path('search/', search, name='search'),

]
