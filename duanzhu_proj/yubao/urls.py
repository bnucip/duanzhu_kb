from django.urls import path
from . import views

urlpatterns = [
    path("points/", views.point_list, name="point_list"),
    path("mono_raw/", views.mono_raw_list, name="mono_raw_list"),
    path("mono/", views.mono_list, name="mono_list"),
    path("consonant_counts/", views.consonant_counts, name="consonant_counts"),
]
