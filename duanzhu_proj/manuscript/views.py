from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import DuanZhu, SwDu
from django.core.paginator import Paginator
from django.db.models import Q

def index(request):
    return render(request, 'index.html')


def catalogue_data(request):
    """Load juan and bushou initially; load zitous dynamically on demand"""
    if 'bushou' in request.GET:
        # Load zitous for the clicked bushou only
        bushou = request.GET['bushou']
        zitous = DuanZhu.objects.filter(bushou=bushou).values_list('id', 'zitou')
        return JsonResponse([
            {"id": str(zitou_id), "text": zitou, "type": "zitou", "children": False} for zitou_id, zitou in zitous
        ], safe=False)

    else:
        # Load juans with bushous (but don't preload zitous)
        juans = DuanZhu.objects.values_list('juan', flat=True).distinct()
        tree_data = []

        for juan in juans:
            bushous = DuanZhu.objects.filter(juan=juan).values_list('bushou', flat=True).distinct()
            bushou_nodes = [{"id": bushou, "text": bushou, "type": "bushou", "children": False} for bushou in bushous]

            tree_data.append({
                "id": juan, "text": juan, "type": "juan", "children": bushou_nodes
            })

        return JsonResponse(tree_data, safe=False)


def zitou_detail(request, zitou_id):
    zitou = get_object_or_404(DuanZhu, id=zitou_id)
    swdu = SwDu.objects.filter(duanzhu=zitou_id).first()

    # Get previous and next zitou in the same bushou
    siblings = DuanZhu.objects.order_by('duanzhu_bianhao')
    prev_zitou = siblings.filter(duanzhu_bianhao__lt=zitou.duanzhu_bianhao).order_by('-duanzhu_bianhao').first()
    next_zitou = siblings.filter(duanzhu_bianhao__gt=zitou.duanzhu_bianhao).order_by('duanzhu_bianhao').first()

    # If AJAX request, return only the main content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, "manuscript/zitou_detail.html", {
            "zitou": zitou,
            "swdu": swdu,
            "prev_zitou": prev_zitou,
            "next_zitou": next_zitou,
        })

    return render(request, "manuscript/index.html", {
        "zitou": zitou,
        "swdu": swdu,
        "prev_zitou": prev_zitou,
        "next_zitou": next_zitou,
    })

def search(request):
    keyword = request.POST.get('keyword', '').strip()
    categ = request.POST.get('categ', '').strip()
    context = {'keyword': keyword, 'categ': categ}
    if keyword:
        data = DuanZhu.objects
        if categ == 'zitou':
            data = data.filter(zitou__in=list(keyword))
        else:
            data = data.filter(zhengwen_zhushi__contains=keyword)
        paginator = Paginator(data.order_by('duanzhu_bianhao'), 10)
        page = request.POST.get('page')
        context['models'] = paginator.get_page(page)
    else:
        context['models'] = []

    return render(request, "manuscript/search.html", context)
