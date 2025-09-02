from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Point, MonoRaw, Mono


def point_list(request):
    points = Point.objects.all().order_by("id")
    paginator = Paginator(points, 100)  # 20 rows per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "yubao/point_list.html", {"page_obj": page_obj})


def mono_raw_list(request):
    raws = MonoRaw.objects.all().order_by("id")
    paginator = Paginator(raws, 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "yubao/mono_raw_list.html", {"page_obj": page_obj})


def mono_list(request):
    old_consonant = request.GET.get('old_consonant')
    young_consonant = request.GET.get('young_consonant')

    monos = Mono.objects.all().order_by("id")

    if old_consonant:
        monos = monos.filter(old_consonant=old_consonant)
    if young_consonant:
        monos = monos.filter(young_consonant=young_consonant)

    paginator = Paginator(monos, 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "yubao/mono_list.html", {"page_obj": page_obj})


def consonant_counts(request):
    # Old consonant counts
    old_counts = (
        Mono.objects
        .values('old_consonant')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Young consonant counts
    young_counts = (
        Mono.objects
        .values('young_consonant')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    context = {
        'old_counts': old_counts,
        'young_counts': young_counts,
    }
    return render(request, 'yubao/consonant_counts.html', context)


