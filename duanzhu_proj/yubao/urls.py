from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="yubao_index"),  # root page of the app
    path("points/", views.point_list, name="point_list"),
    path("mono_raw/", views.mono_raw_list, name="mono_raw_list"),
    path("mono/", views.mono_list, name="mono_list"),
    path("consonant_counts/", views.consonant_counts, name="consonant_counts"),
    path("mono_raw/edit/", views.mono_raw_edit, name="mono_raw_edit"),
    path("rebuild_mono/", views.rebuild_mono, name="rebuild_mono"),
]
