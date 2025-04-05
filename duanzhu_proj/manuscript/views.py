from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from .models import DuanZhu, SwDu, Gujinzi, Guyunbu, Gouyi, Yinyitong, Yinshu, Zhishimulu, Liushu, Zhuanzhu, Jiajie, \
    Tongzi, Xingfeizi, Huxun, Zhiyan, Lianmianci, Yinshen, Benyi, Gujinyi
from django.core.paginator import Paginator

def index(request):
    context = {}
    if 'id' in request.GET:  # 先检查参数是否存在
        zitou_id = request.GET['id']
        try:
            zitou = get_object_or_404(DuanZhu, id=zitou_id)
            context['zitou'] = zitou
        except ValidationError:
            raise Http404

    return render(request, 'index.html',context)


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

def zstag_detail(request, zitou_id, tag):
    context = {"tag":tag}
    if(tag=='wz'):
        gujinzis = list(Gujinzi.objects.filter(duanzhu=zitou_id))
        for gujinzi in gujinzis:
            gujinzi.miaoshu = gujinzi.miaoshu.replace("古字:","").replace("今字:","").split("；")
        context['gujinzis'] = gujinzis
    elif(tag=='yy'):
        guyunbus = list(Guyunbu.objects.filter(duanzhu=zitou_id))
        context['guyunbus'] = guyunbus
    elif(tag == 'xg'):
        gouyis = list(Gouyi.objects.filter(duanzhu=zitou_id))
        context['gouyis'] = gouyis
        zitou = get_object_or_404(DuanZhu, id=zitou_id)
        yinyitongs = list(Yinyitong.objects.filter(object1_duanzhu_bianhao=zitou.duanzhu_bianhao))
        context['yinyitongs'] = yinyitongs
    elif (tag == 'ys'):
        zitou = get_object_or_404(DuanZhu, id=zitou_id)
        yinshus = list(Yinshu.objects.filter(duanzhu_bianhaos__contains=zitou.duanzhu_bianhao))
        context['yinshus'] = yinshus
    return render(request, "manuscript/zstag_detail.html", context)


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

def yinyitong(request):
    context = {}
    data = Yinyitong.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu1 = DuanZhu.objects.filter(duanzhu_bianhao=p.object1_duanzhu_bianhao).first()
        if duanzhu1:
            duanzhu1.zhengwen_zhushi = duanzhu1.zhengwen_zhushi.replace(p.duanshianyu,'<span>' + p.duanshianyu + '</span>')
            p.duanzhu1 = duanzhu1
        duanzhu2 = DuanZhu.objects.filter(duanzhu_bianhao=p.object2_duanzhu_bianhao).first()
        if duanzhu2:
            duanzhu2.zhengwen_zhushi = duanzhu2.zhengwen_zhushi.replace(p.duanshianyu, '<span>' + p.duanshianyu + '</span>')
            p.duanzhu2 = duanzhu2
    context['models'] = page_obj

    return render(request, "manuscript/yinyitong.html", context)

def zhishimulu_data(request):
    level1s = list(Zhishimulu.objects.filter(level=1))
    tree_data = []
    for level1 in level1s:
        level2s = Zhishimulu.objects.filter(parent_id=level1.id).values_list('id','tag_name')
        level2_nades = []
        print(level2s)
        for level2 in level2s:
            level3s = Zhishimulu.objects.filter(parent_id=level2[0]).values_list('id','tag_name','url')
            level3_nodes = [{"id": id, "text": tag_name, "url":url, "type": "level3", "children": False} for id,tag_name,url in level3s]
            level2_node = {"id": level2[0], "text": level2[1], "type": "level2", "children": level3_nodes}
            level2_nades.append(level2_node)
        tree_data.append({
            "id": level1.id, "text": level1.tag_name, "type": "level1", "children": level2_nades
        })

    return JsonResponse(tree_data, safe=False)

def xiangxing(request):
    context = {}
    data = Liushu.objects.filter(liushu='象形')
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/xiangxing.html", context)

def zhishi(request):
    context = {}
    data = Liushu.objects.filter(liushu='指事')
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zhishi.html", context)

def huiyi(request):
    context = {}
    data = Liushu.objects.filter(liushu='会意')
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/huiyi.html", context)

def xingsheng(request):
    context = {}
    data = Liushu.objects.filter(liushu='形声')
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/xingsheng.html", context)

def zhuanzhu(request):
    context = {}
    data = Zhuanzhu.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.zhuanzhu, '<span>' + p.zhuanzhu + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zhuanzhu.html", context)

def jiajie(request):
    context = {}
    data = Jiajie.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.jiajiezhuwen, '<span>' + p.jiajiezhuwen + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/jiajie.html", context)

def tongzi(request):
    context = {}
    data = Tongzi.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.tongzizhuwen, '<span>' + p.tongzizhuwen + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/tongzi.html", context)

def xingfeizi(request):
    context = {}
    data = Xingfeizi.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.pipeizifuchuan, '<span>' + p.pipeizifuchuan + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/xingfeizi.html", context)

def huxun(request):
    context = {}
    data = Huxun.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.shuojie, '<span>' + p.shuojie + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/huxun.html", context)

def zhiyan(request):
    context = {}
    data = Zhiyan.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.zhiyanshuojie, '<span>' + p.zhiyanshuojie + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zhiyan.html", context)

def lianmianci(request):
    context = {}
    data = Lianmianci.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/lianmianci.html", context)

def yinshen(request):
    context = {}
    data = Yinshen.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.yinshen, '<span>' + p.yinshen + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yinshen.html", context)

def benyi(request):
    context = {}
    data = Benyi.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.benyi_1, '<span>' + p.benyi_1 + '</span>')
        if p.benyi_2:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.benyi_2, '<span>' + p.benyi_2 + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/benyi.html", context)

def gujinyi(request):
    context = {}
    data = Gujinyi.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.shuojie, '<span>' + p.shuojie + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/gujinyi.html", context)

def gouyi(request):
    context = {}
    data = Gouyi.objects.all()
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        if p.gouyi1:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi1, '<span>' + p.gouyi1 + '</span>')
        if p.gouyi2:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi2, '<span>' + p.gouyi2 + '</span>')
        if p.gouyi3:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi3, '<span>' + p.gouyi3 + '</span>')
        if p.shengfugouyi:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.shengfugouyi, '<span>' + p.shengfugouyi + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/gouyi.html", context)
