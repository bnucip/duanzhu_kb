import json
import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, OuterRef, Exists
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from .models import DuanZhu, SwDu, Gujinzi, Guyunbu, Gouyi, Yinyitong, Yinshu, Zhishimulu, Liushu, Zhuanzhu, Jiajie, \
    Tongzi, Xingfeizi, Huxun, Zhiyan, Lianmianci, Yinshen, Benyi, Gujinyi, Hunyanxiyan, Ezi, Suzi, Suiwen, You, Shuozi, \
    Feishi, Fanxun, Tongxun, Shuangsheng, Dieyun, Yijinshigu, Hujian, Guyu, Shengfushiyuan, Fangsu, Tongyu, Zhuanyu, \
    Yixiangzu, Yintongyiyi, Bieyiyi, Guyin, Jinyin, Yinzhuan, Yinbian, Zuijin, Guheyun, Yiwen, Shan, Duotuo, Wanggai, \
    Zheng, Benzuo, Xingfeiyi, KnowledgeAnnotate, RelationKnowledge, SingleObjectKnowledge
from django.core.paginator import Paginator

def index(request):
    return render(request, 'home.html')

def zitou(request):
    context = {}
    if 'id' in request.GET:  # 先检查参数是否存在
        zitou_id = request.GET['id']
        try:
            zitou = get_object_or_404(DuanZhu, id=zitou_id)
            context['zitou'] = zitou
        except ValidationError:
            raise Http404
    if 'zitou' in request.GET:  # 先检查参数是否存在
        zitou = request.GET['zitou']
        try:
            zitou = get_object_or_404(DuanZhu, zitou=zitou)
            context['zitou'] = zitou
        except ValidationError:
            raise Http404

    return render(request, 'zitou.html',context)

# def knowledge_guide_search(request):
#     return render(request, 'manuscript/knowledge_guide_search.html')


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

    return render(request, "manuscript/zitou.html", {
        "zitou": zitou,
        "swdu": swdu,
        "prev_zitou": prev_zitou,
        "next_zitou": next_zitou,
    })

def zstag_detail(request, zitou_id, tag):
    context = {"tag":tag}
    if(tag=='wz'):
        xiangxings = Liushu.objects.filter(liushu='象形',duanzhu=zitou_id)
        context['xiangxings'] = xiangxings
        zhishis = Liushu.objects.filter(liushu='指事', duanzhu=zitou_id)
        context['zhishis'] = zhishis
        huiyis = Liushu.objects.filter(liushu='会意', duanzhu=zitou_id)
        context['huiyis'] = huiyis
        zhuanzhus = Zhuanzhu.objects.filter(duanzhu=zitou_id)
        context['zhuanzhus'] = zhuanzhus
        xingshengs = Liushu.objects.filter(liushu='形声',duanzhu=zitou_id)
        context['xingshengs'] = xingshengs
        jiajies = Jiajie.objects.filter(duanzhu=zitou_id)
        context['jiajies'] = jiajies

        xingfeizis = list(Xingfeizi.objects.filter(duanzhu=zitou_id))
        context['xingfeizis'] = xingfeizis
        ezis = list(Ezi.objects.filter(duanzhu=zitou_id))
        context['ezis'] = ezis
        suzis = list(Suzi.objects.filter(duanzhu=zitou_id))
        context['suzis'] = suzis
        tongzis = list(Tongzi.objects.filter(duanzhu=zitou_id))
        context['tongzis'] = tongzis
        gujinzis = list(Gujinzi.objects.filter(duanzhu=zitou_id))
        # for gujinzi in gujinzis:
        #     gujinzi.miaoshu = gujinzi.miaoshu.replace("古字:","").replace("今字:","").split("；")
        context['gujinzis'] = gujinzis
    elif(tag=='yy'):
        guyunbus = list(Guyunbu.objects.filter(duanzhu=zitou_id))
        context['guyunbus'] = guyunbus
        guyins = list(Guyin.objects.filter(duanzhu=zitou_id))
        context['guyins'] = guyins
        jinyins = list(Jinyin.objects.filter(duanzhu=zitou_id))
        context['jinyins'] = jinyins
        yinzhuans = list(Yinzhuan.objects.filter(duanzhu=zitou_id))
        context['yinzhuans'] = yinzhuans
        yinbians = list(Yinbian.objects.filter(duanzhu=zitou_id))
        context['yinbians'] = yinbians
        zuijins = list(Zuijin.objects.filter(duanzhu=zitou_id))
        context['zuijins'] = zuijins
        guheyuns = list(Guheyun.objects.filter(duanzhu=zitou_id))
        context['guheyuns'] = guheyuns
    elif(tag == 'xg'):
        yous = list(You.objects.filter(duanzhu=zitou_id))
        context['yous'] = yous
        gouyis = list(Gouyi.objects.filter(duanzhu=zitou_id))
        context['gouyis'] = gouyis
        suiwens = list(Suiwen.objects.filter(duanzhu=zitou_id))
        context['suiwens'] = suiwens
        shuozis = list(Shuozi.objects.filter(duanzhu=zitou_id))
        context['shuozis'] = shuozis
        feishis = list(Feishi.objects.filter(duanzhu=zitou_id))
        context['feishis'] = feishis
        fanxuns = list(Fanxun.objects.filter(duanzhu=zitou_id))
        context['fanxuns'] = fanxuns
        tongxuns = list(Tongxun.objects.filter(duanzhu=zitou_id))
        context['tongxuns'] = tongxuns
        huxuns = list(Huxun.objects.filter(duanzhu=zitou_id))
        context['huxuns'] = huxuns
        shuangshengs = list(Shuangsheng.objects.filter(duanzhu=zitou_id))
        context['shuangshengs'] = shuangshengs
        dieyuns = list(Dieyun.objects.filter(duanzhu=zitou_id))
        context['dieyuns'] = dieyuns
        yijinshigus = list(Yijinshigu.objects.filter(duanzhu=zitou_id))
        context['yijinshigus'] = yijinshigus
        hujians = list(Hujian.objects.filter(duanzhu=zitou_id))
        context['hujians'] = hujians

        guyus = list(Guyu.objects.filter(duanzhu=zitou_id))
        context['guyus'] = guyus
        hunyanxiyans = list(Hunyanxiyan.objects.filter(duanzhu=zitou_id))
        context['hunyanxiyans'] = hunyanxiyans
        shengfushiyuans = list(Shengfushiyuan.objects.filter(duanzhu=zitou_id))
        context['shengfushiyuans'] = shengfushiyuans
        zhiyans = list(Zhiyan.objects.filter(duanzhu=zitou_id))
        context['zhiyans'] = zhiyans
        lianmiancis = list(Lianmianci.objects.filter(duanzhu=zitou_id))
        context['lianmiancis'] = lianmiancis
        fangsus = list(Fangsu.objects.filter(duanzhu=zitou_id))
        context['fangsus'] = fangsus
        tongyus = list(Tongyu.objects.filter(duanzhu=zitou_id))
        context['tongyus'] = tongyus
        zhuanyus = list(Zhuanyu.objects.filter(duanzhu=zitou_id))
        context['zhuanyus'] = zhuanyus

        yinshens = list(Yinshen.objects.filter(duanzhu=zitou_id))
        context['yinshens'] = yinshens
        benyis = list(Benyi.objects.filter(duanzhu=zitou_id))
        context['benyis'] = benyis
        gujinyis = list(Gujinyi.objects.filter(duanzhu=zitou_id))
        context['gujinyis'] = gujinyis
        yixiangzus = list(Yixiangzu.objects.filter(duanzhu=zitou_id))
        context['yixiangzus'] = yixiangzus
        zitou = get_object_or_404(DuanZhu, id=zitou_id)
        yinyitongs = list(Yinyitong.objects.filter(object1_duanzhu_bianhao=zitou.duanzhu_bianhao))
        context['yinyitongs'] = yinyitongs
        yintongyiyis = list(Yintongyiyi.objects.filter(duanzhu=zitou_id))
        context['yintongyiyis'] = yintongyiyis
        bieyiyis = list(Bieyiyi.objects.filter(duanzhu=zitou_id))
        context['bieyiyis'] = bieyiyis
    elif (tag == 'xk'):
        yiwens = list(Yiwen.objects.filter(duanzhu=zitou_id))
        context['yiwens'] = yiwens
        shans = list(Shan.objects.filter(duanzhu=zitou_id))
        context['shans'] = shans
        duotuos = list(Duotuo.objects.filter(duanzhu=zitou_id))
        context['duotuos'] = duotuos
        wanggais = list(Wanggai.objects.filter(duanzhu=zitou_id))
        context['wanggais'] = wanggais
        zhengs = list(Zheng.objects.filter(duanzhu=zitou_id))
        context['zhengs'] = zhengs
        benzuos = list(Benzuo.objects.filter(duanzhu=zitou_id))
        context['benzuos'] = benzuos
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
        if categ == 'zitou':
            data = DuanZhu.objects
            data = data.filter(zitou__in=list(keyword))
            paginator = Paginator(data.order_by('duanzhu_bianhao'), 10)
        elif categ =='quanwen':
            data = DuanZhu.objects
            data = data.filter(zhengwen_zhushi__contains=keyword)
            paginator = Paginator(data.order_by('duanzhu_bianhao'), 10)
        # else:
        #     data = Zhishimulu.objects
        #     data = data.filter(shuyuxingshi__contains=keyword)
        #     paginator = Paginator(data,10)
        page = request.POST.get('page')
        page_obj = paginator.get_page(page)
        for p in page_obj:
            swdu = SwDu.objects.filter(duanzhu=p.id).first()
            if swdu:
                p.swdu = swdu
        context['models'] = page_obj
    else:
        context['models'] = []

    return render(request, "manuscript/search.html", context)

def zstxSearch(request):
    keyword = request.POST.get('keyword', '').strip()
    context = {'keyword': keyword}
    if keyword:
        data = Zhishimulu.objects
        data = data.filter(Q(shuyuxingshi__contains=keyword)|Q(shuyuxingshi_jian__contains=keyword))
        paginator = Paginator(data,10)
        page = request.POST.get('page')
        page_obj = paginator.get_page(page)
        context['models'] = page_obj
    else:
        context['models'] = []

    return render(request, "manuscript/zstxSearch.html", context)

# def yinyitong(request):
#     context = {}
#     data = Yinyitong.objects.all()
#     paginator = Paginator(data, 10)
#     page = request.GET.get('page')
#     page_obj = paginator.get_page(page)
#     for p in page_obj:
#         duanzhu1 = DuanZhu.objects.filter(duanzhu_bianhao=p.object1_duanzhu_bianhao).first()
#         if duanzhu1:
#             duanzhu1.zhengwen_zhushi = duanzhu1.zhengwen_zhushi.replace(p.duanshianyu,'<span>' + p.duanshianyu + '</span>')
#             p.duanzhu1 = duanzhu1
#         duanzhu2 = DuanZhu.objects.filter(duanzhu_bianhao=p.object2_duanzhu_bianhao).first()
#         if duanzhu2:
#             duanzhu2.zhengwen_zhushi = duanzhu2.zhengwen_zhushi.replace(p.duanshianyu, '<span>' + p.duanshianyu + '</span>')
#             p.duanzhu2 = duanzhu2
#     context['models'] = page_obj
#
#     return render(request, "manuscript/yinyitong.html", context)

def yinyitong(request):
    context = {}
    items = []
    filterData = []
    data = Yinyitong.objects.all()
    for item in data:
        if item.object1_duanzhu_bianhao not in items:
            items.append(item.object1_duanzhu_bianhao)
            filterData.append(item)
    paginator = Paginator(filterData, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu1 = DuanZhu.objects.filter(duanzhu_bianhao=p.object1_duanzhu_bianhao).first()
        if duanzhu1:
            duanzhu1.zhengwen_zhushi = duanzhu1.zhengwen_zhushi.replace(p.duanshianyu,'<span>' + p.duanshianyu + '</span>')
            p.duanzhu1 = duanzhu1
        relList = list(Yinyitong.objects.filter(object1_duanzhu_bianhao=p.object1_duanzhu_bianhao))
        for rel in relList:
            dz = DuanZhu.objects.filter(duanzhu_bianhao=rel.object2_duanzhu_bianhao).first()
            if dz:
                dz.zhengwen_zhushi = dz.zhengwen_zhushi.replace(rel.duanshianyu, '<span>' + rel.duanshianyu + '</span>')
                rel.dz = dz
        p.relList = relList
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        if p.match_content:
            for content in p.match_content.split("#"):
                duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(content, '<span>' + content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/benyi.html", context)

def gujinyi(request):
    context = {}
    data = Gujinyi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
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
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        if p.match_content:
            for content in p.match_content.split("#"):
                duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(content, '<span>' + content + '</span>')
        # if p.gouyi1:
        #     duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi1, '<span>' + p.gouyi1 + '</span>')
        # if p.gouyi2:
        #     duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi2, '<span>' + p.gouyi2 + '</span>')
        # if p.gouyi3:
        #     duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.gouyi3, '<span>' + p.gouyi3 + '</span>')
        # if p.shengfugouyi:
        #     duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.shengfugouyi, '<span>' + p.shengfugouyi + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/gouyi.html", context)

def gujinzi(request):
    context = {}
    data = Gujinzi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
        if p.guzi_id:
            duanzhu1 = DuanZhu.objects.filter(duanzhu_bianhao=p.guzi_id).first()
            p.duanzhu1 = duanzhu1
        if p.jinzi_id:
            duanzhu2 = DuanZhu.objects.filter(duanzhu_bianhao=p.jinzi_id).first()
            p.duanzhu2 = duanzhu2
    context['models'] = page_obj
    return render(request, "manuscript/gujinzi.html", context)

def hunyanxiyan(request):
    context = {}
    data = Hunyanxiyan.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        p.duanzhu = duanzhu
        if p.obj1_duanzhu_id:
            duanzhu1 = DuanZhu.objects.filter(duanzhu_bianhao=p.obj1_duanzhu_id).first()
            p.duanzhu1 = duanzhu1
        if p.obj2_duanzhu_id:
            duanzhu2 = DuanZhu.objects.filter(duanzhu_bianhao=p.obj2_duanzhu_id).first()
            p.duanzhu2 = duanzhu2
        if p.obj3_duanzhu_id:
            duanzhu3 = DuanZhu.objects.filter(duanzhu_bianhao=p.obj3_duanzhu_id).first()
            p.duanzhu3 = duanzhu3
        if p.obj4_duanzhu_id:
            duanzhu4 = DuanZhu.objects.filter(duanzhu_bianhao=p.obj4_duanzhu_id).first()
            p.duanzhu4 = duanzhu4
        if p.obj5_duanzhu_id:
            duanzhu5 = DuanZhu.objects.filter(duanzhu_bianhao=p.obj5_duanzhu_id).first()
            p.duanzhu5 = duanzhu5
    context['models'] = page_obj
    return render(request, "manuscript/hunyanxiyan.html", context)

def ezi(request):
    context = {}
    data = Ezi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/ezi.html", context)

def suzi(request):
    context = {}
    data = Suzi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/suzi.html", context)

def you(request):
    context = {}
    data = You.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/you.html", context)

def suiwen(request):
    context = {}
    data = Suiwen.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/suiwen.html", context)

def shuozi(request):
    context = {}
    data = Shuozi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/shuozi.html", context)

def feishi(request):
    context = {}
    data = Feishi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/feishi.html", context)

def fanxun(request):
    context = {}
    data = Fanxun.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/fanxun.html", context)

def tongxun(request):
    context = {}
    data = Tongxun.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/tongxun.html", context)

def shuangsheng(request):
    context = {}
    data = Shuangsheng.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/shuangsheng.html", context)

def dieyun(request):
    context = {}
    data = Dieyun.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/dieyun.html", context)

def yijinshigu(request):
    context = {}
    data = Yijinshigu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yijinshigu.html", context)

def hujian(request):
    context = {}
    data = Hujian.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/hujian.html", context)

def guyu(request):
    context = {}
    data = Guyu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/guyu.html", context)

def shengfushiyuan(request):
    context = {}
    data = Shengfushiyuan.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/shengfushiyuan.html", context)

def fangsu(request):
    context = {}
    data = Fangsu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/fangsu.html", context)

def tongyu(request):
    context = {}
    data = Tongyu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/tongyu.html", context)

def zhuanyu(request):
    context = {}
    data = Zhuanyu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zhuanyu.html", context)

def yixiangzu(request):
    context = {}
    data = Yixiangzu.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yixiangzu.html", context)

def yintongyiyi(request):
    context = {}
    data = Yintongyiyi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yintongyiyi.html", context)

def bieyiyi(request):
    context = {}
    data = Bieyiyi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/bieyiyi.html", context)


def guyin(request):
    context = {}
    data = Guyin.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/guyin.html", context)

def jinyin(request):
    context = {}
    data = Jinyin.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/jinyin.html", context)

def yinzhuan(request):
    context = {}
    data = Yinzhuan.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yinzhuan.html", context)

def yinbian(request):
    context = {}
    data = Yinbian.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yinbian.html", context)

def zuijin(request):
    context = {}
    data = Zuijin.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zuijin.html", context)

def guheyun(request):
    context = {}
    data = Guheyun.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/guheyun.html", context)

def yiwen(request):
    context = {}
    data = Yiwen.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/yiwen.html", context)

def shan(request):
    context = {}
    data = Shan.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/shan.html", context)

def duotuo(request):
    context = {}
    data = Duotuo.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        if p.match_content:
            for content in p.match_content.split("#"):
                duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(content, '<span>' + content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/duotuo.html", context)

def wanggai(request):
    context = {}
    data = Wanggai.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/wanggai.html", context)

def zheng(request):
    context = {}
    data = Zheng.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/zheng.html", context)

def benzuo(request):
    context = {}
    data = Benzuo.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content, '<span>' + p.match_content + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/benzuo.html", context)

def xingfeiyi(request):
    context = {}
    data = Xingfeiyi.objects.all()
    paginator = Paginator(data, 10)
    id = request.GET.get('id')
    if id:
        position = data.filter(id__lte=id).count()
        page = (position - 1) // 10 + 1
    else:
        page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    for p in page_obj:
        duanzhu = DuanZhu.objects.filter(duanzhu_bianhao=p.duanzhu_bianhao).first()
        duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.yixingyifeishuojie, '<span>' + p.yixingyifeishuojie + '</span>')
        p.duanzhu = duanzhu
    context['models'] = page_obj

    return render(request, "manuscript/xingfeiyi.html", context)

def yunbu(request):
    context = {}
    return render(request, "manuscript/yunbu.html", context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # return redirect('mark')
            next_url = request.GET.get('next', '/mark/')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def mark(request):
    context = {}
    user = request.user
    context['user'] = user
    print(user.username)
    juans = []
    juanNames = DuanZhu.objects.values_list('juan', flat=True).distinct()
    for juanName in juanNames:
        juan = {}
        juan['name'] = juanName
        juan['status'] = 1
        juans.append(juan)
    context['juans'] = juans
    return render(request, 'manuscript/mark.html', context)

@login_required
def getZitous(request):
    juan = request.GET['juan']
    zitous = list(DuanZhu.objects.filter(juan=juan).values_list('id','zitou','status'))
    return JsonResponse(zitous, safe=False)

@login_required
def getZitouParagraphs(request):
    zt = request.GET['zitou']
    zitou = get_object_or_404(DuanZhu, zitou=zt)
    pattern = r'<([pz]\d+)>(.*?)</\1>'
    result = re.findall(pattern, zitou.zhengwen_zhushi)
    data = [{"position": item[0], "content": item[1], "bzContent":''} for item in result]
    if zitou.zhengwen_zhushi_bz :
        bzResult = re.findall(pattern, zitou.zhengwen_zhushi_bz)
        for i,item in enumerate(data):
            item["bzContent"] = bzResult[i][1]
    # print(data)
    return JsonResponse(data, safe=False)

@login_required
def bzZitou(request):
    context = {}
    success = False
    user = request.user
    if user:
        try:
            currentTime = datetime.now()
            print(user.id)
            print(currentTime)
            if request.method == 'POST':
                param = json.loads(request.body)
                # print(param)
                zitouId = param.get("zitouId")
                zitou = get_object_or_404(DuanZhu, id=zitouId)
                if zitou:
                    bzcontent = ""
                    segments = param.get("data")
                    for item in segments:
                        bzcontent += "<" + item["position"] + ">" + item["bzContent"] + "</" + item["position"] + ">"
                    # print(bzcontent)
                    zitou.zhengwen_zhushi_bz = bzcontent
                    zitou.status = 1
                    zitou.user_id = user.id
                    zitou.update_time = currentTime
                    zitou.save()
                    success = True
        except Exception as e:
            print(e)
    context["success"] = success

    return JsonResponse(context, safe=False)

@login_required
def knowledge(request):
    context = {}
    level1s = list(Zhishimulu.objects.filter(level=1))
    tree_data = []
    for level1 in level1s:
        level2s = Zhishimulu.objects.filter(parent_id=level1.id).values_list('id','tag_name')
        level2_nades = []
        print(level2s)
        for level2 in level2s:
            level3s = Zhishimulu.objects.filter(parent_id=level2[0]).values_list('id','tag_name','url','shuxing','shuyuxingshi')
            level3_nodes = [{"id": id, "text": tag_name, "url":url, "type": "level3", "shuxing":shuxing,"shuyuxingshi":shuyuxingshi, "children": False} for id,tag_name,url,shuxing,shuyuxingshi in level3s]
            level2_node = {"id": level2[0], "text": level2[1], "type": "level2", "children": level3_nodes}
            level2_nades.append(level2_node)
        tree_data.append({
            "id": level1.id, "text": level1.tag_name, "type": "level1", "children": level2_nades
        })
        context['mulus'] = tree_data

    return render(request, "manuscript/zhishimulu.html", context)

@login_required
def editKnowledge(request):
    context = {}
    success = False
    user = request.user
    if user:
        try:
            if request.method == 'POST':
                param = json.loads(request.body)
                id = param.get("id")
                tagName = param.get("tagName")
                zhishiji = param.get("zhishiji")
                shuyu = param.get("shuyu")
                shuxing = param.get("shuxing")
                zsmlZSJ = Zhishimulu.objects.filter(tag_name=zhishiji).first()
                if id:
                    if id == "yunbu":
                        print("yunbu")
                    else:
                        zhishimulu = get_object_or_404(Zhishimulu, id=id)
                        if zhishimulu:

                            zhishimulu.parent_id = zsmlZSJ.id
                            zhishimulu.shuyu = shuyu
                            zhishimulu.shuxing = shuxing
                            zhishimulu.save()
                            success = True
                else:
                    Zhishimulu.objects.create(tag_name=tagName, parent_id=zsmlZSJ.id, level=3, shuyuxingshi=shuyu, shuxing=shuxing)
                    success = True
        except Exception as e:
            print(e)
    context["success"] = success

    return JsonResponse(context, safe=False)

@login_required
def knowledgeAnnotate1(request):
    knowledgePoint = request.GET.get("knowledgePoint")
    print(knowledgePoint)
    context = {}
    context['knowledgePoint'] = knowledgePoint

    return render(request, "manuscript/zhishimulu_annotate1.html", context)

@login_required
def knowledgeAnnotate2(request):
    knowledgePoint = request.GET.get("knowledgePoint")
    print(knowledgePoint)
    context = {}
    context['knowledgePoint'] = knowledgePoint

    return render(request, "manuscript/zhishimulu_annotate2.html", context)

@login_required
def saveKnowledgeAnnotate1(request):
    context = {}
    success = False
    user = request.user
    if user:
        try:
            if request.method == 'POST':
                param = json.loads(request.body)
                id = param.get("id")
                knowledgePoint = param.get("knowledgePoint")
                belongsToPoint = param.get("belongsToPoint")
                zhishimiaoshu = param.get("zhishimiaoshu")
                bianhao = param.get("bianhao")

                if knowledgePoint == "象形":
                    xiangxing = Liushu.objects.filter(duanzhu_id=id, liushu='象形').first()
                    if xiangxing:
                        if belongsToPoint == "1":
                            xiangxing.zhishimiaoshu = zhishimiaoshu
                            xiangxing.save()
                        else:
                            xiangxing.delete()
                    else:
                        if belongsToPoint == "1":
                            Liushu.objects.create(duanzhu_bianhao=bianhao,liushu="象形",duanzhu_id=id,zhishimiaoshu=zhishimiaoshu)
                elif knowledgePoint == "指事":
                    zhishi = Liushu.objects.filter(duanzhu_id=id, liushu='指事').first()
                    if zhishi:
                        if belongsToPoint == "1":
                            zhishi.zhishimiaoshu = zhishimiaoshu
                            zhishi.save()
                        else:
                            zhishi.delete()
                    else:
                        if belongsToPoint == "1":
                            Liushu.objects.create(duanzhu_bianhao=bianhao,liushu="zhishi",duanzhu_id=id,zhishimiaoshu=zhishimiaoshu)
                elif knowledgePoint == "会意":
                    huiyi = Liushu.objects.filter(duanzhu_id=id, liushu='会意').first()
                    if huiyi:
                        if belongsToPoint == "1":
                            huiyi.zhishimiaoshu = zhishimiaoshu
                            huiyi.save()
                        else:
                            huiyi.delete()
                    else:
                        if belongsToPoint == "1":
                            Liushu.objects.create(duanzhu_bianhao=bianhao,liushu="会意",duanzhu_id=id,zhishimiaoshu=zhishimiaoshu)
                elif knowledgePoint == "犹":
                    you = You.objects.filter(duanzhu_id=id).first()
                    if you:
                        if belongsToPoint == "1":
                            you.match_content = zhishimiaoshu
                            you.save()
                        else:
                            you.delete()
                    else:
                        if belongsToPoint == "1":
                            You.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "构意":
                    gouyi = Gouyi.objects.filter(duanzhu_id=id).first()
                    if gouyi:
                        if belongsToPoint == "1":
                            gouyi.match_content = zhishimiaoshu
                            gouyi.save()
                        else:
                            gouyi.delete()
                    else:
                        if belongsToPoint == "1":
                            Gouyi.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "随文解之":
                    suiwen = Suiwen.objects.filter(duanzhu_id=id).first()
                    if suiwen:
                        if belongsToPoint == "1":
                            suiwen.match_content = zhishimiaoshu
                            suiwen.save()
                        else:
                            suiwen.delete()
                    else:
                        if belongsToPoint == "1":
                            Suiwen.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "说字训诂":
                    shuozi = Shuozi.objects.filter(duanzhu_id=id).first()
                    if shuozi:
                        if belongsToPoint == "1":
                            shuozi.match_content = zhishimiaoshu
                            shuozi.save()
                        else:
                            shuozi.delete()
                    else:
                        if belongsToPoint == "1":
                            Shuozi.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "非是":
                    feishi = Feishi.objects.filter(duanzhu_id=id).first()
                    if feishi:
                        if belongsToPoint == "1":
                            feishi.match_content = zhishimiaoshu
                            feishi.save()
                        else:
                            feishi.delete()
                    else:
                        if belongsToPoint == "1":
                            Feishi.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "古语":
                    guyu = Guyu.objects.filter(duanzhu_id=id).first()
                    if guyu:
                        if belongsToPoint == "1":
                            guyu.match_content = zhishimiaoshu
                            guyu.save()
                        else:
                            guyu.delete()
                    else:
                        if belongsToPoint == "1":
                            Guyu.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "声符示源":
                    shengfushiyuan = Shengfushiyuan.objects.filter(duanzhu_id=id).first()
                    if shengfushiyuan:
                        if belongsToPoint == "1":
                            shengfushiyuan.match_content = zhishimiaoshu
                            shengfushiyuan.save()
                        else:
                            shengfushiyuan.delete()
                    else:
                        if belongsToPoint == "1":
                            Shengfushiyuan.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,match_content=zhishimiaoshu)
                elif knowledgePoint == "联绵词":
                    lianmianci = Lianmianci.objects.filter(duanzhu_id=id).first()
                    if lianmianci:
                        if belongsToPoint == "1":
                            lianmianci.lianmianci = zhishimiaoshu
                            lianmianci.save()
                        else:
                            lianmianci.delete()
                    else:
                        if belongsToPoint == "1":
                            Lianmianci.objects.create(duanzhu_bianhao=bianhao,duanzhu_id=id,lianmianci=zhishimiaoshu)
                elif knowledgePoint == "方言俗语":
                    fangsu = Fangsu.objects.filter(duanzhu_id=id).first()
                    if fangsu:
                        if belongsToPoint == "1":
                            fangsu.match_content = zhishimiaoshu
                            fangsu.save()
                        else:
                            fangsu.delete()
                    else:
                        if belongsToPoint == "1":
                            Fangsu.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "通语":
                    tongyu = Tongyu.objects.filter(duanzhu_id=id).first()
                    if tongyu:
                        if belongsToPoint == "1":
                            tongyu.match_content = zhishimiaoshu
                            tongyu.save()
                        else:
                            tongyu.delete()
                    else:
                        if belongsToPoint == "1":
                            Tongyu.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "转语":
                    zhuanyu = Zhuanyu.objects.filter(duanzhu_id=id).first()
                    if zhuanyu:
                        if belongsToPoint == "1":
                            zhuanyu.match_content = zhishimiaoshu
                            zhuanyu.save()
                        else:
                            zhuanyu.delete()
                    else:
                        if belongsToPoint == "1":
                            Zhuanyu.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "本义":
                    benyi = Benyi.objects.filter(duanzhu_id=id).first()
                    if benyi:
                        if belongsToPoint == "1":
                            benyi.match_content = zhishimiaoshu
                            benyi.save()
                        else:
                            benyi.delete()
                    else:
                        if belongsToPoint == "1":
                            Benyi.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "别一义":
                    bieyiyi = Bieyiyi.objects.filter(duanzhu_id=id).first()
                    if bieyiyi:
                        if belongsToPoint == "1":
                            bieyiyi.match_content = zhishimiaoshu
                            bieyiyi.save()
                        else:
                            bieyiyi.delete()
                    else:
                        if belongsToPoint == "1":
                            Bieyiyi.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "古音":
                    guyin = Guyin.objects.filter(duanzhu_id=id).first()
                    if guyin:
                        if belongsToPoint == "1":
                            guyin.match_content = zhishimiaoshu
                            guyin.save()
                        else:
                            guyin.delete()
                    else:
                        if belongsToPoint == "1":
                            Guyin.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "今音":
                    jinyin = Jinyin.objects.filter(duanzhu_id=id).first()
                    if jinyin:
                        if belongsToPoint == "1":
                            jinyin.match_content = zhishimiaoshu
                            jinyin.save()
                        else:
                            jinyin.delete()
                    else:
                        if belongsToPoint == "1":
                            Jinyin.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "删":
                    shan = Shan.objects.filter(duanzhu_id=id).first()
                    if shan:
                        if belongsToPoint == "1":
                            shan.match_content = zhishimiaoshu
                            shan.save()
                        else:
                            shan.delete()
                    else:
                        if belongsToPoint == "1":
                            Shan.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "夺":
                    duotuo = Duotuo.objects.filter(duanzhu_id=id).first()
                    if duotuo:
                        if belongsToPoint == "1":
                            duotuo.match_content = zhishimiaoshu
                            duotuo.save()
                        else:
                            duotuo.delete()
                    else:
                        if belongsToPoint == "1":
                            Duotuo.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "妄改":
                    wanggai = Wanggai.objects.filter(duanzhu_id=id).first()
                    if wanggai:
                        if belongsToPoint == "1":
                            wanggai.match_content = zhishimiaoshu
                            wanggai.save()
                        else:
                            wanggai.delete()
                    else:
                        if belongsToPoint == "1":
                            Wanggai.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "正":
                    zheng = Zheng.objects.filter(duanzhu_id=id).first()
                    if zheng:
                        if belongsToPoint == "1":
                            zheng.match_content = zhishimiaoshu
                            zheng.save()
                        else:
                            zheng.delete()
                    else:
                        if belongsToPoint == "1":
                            Zheng.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                elif knowledgePoint == "本作":
                    benzuo = Benzuo.objects.filter(duanzhu_id=id).first()
                    if benzuo:
                        if belongsToPoint == "1":
                            benzuo.match_content = zhishimiaoshu
                            benzuo.save()
                        else:
                            benzuo.delete()
                    else:
                        if belongsToPoint == "1":
                            Benzuo.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu)
                else:
                    singleObjectKnowledge = SingleObjectKnowledge.objects.filter(duanzhu_id=id, knowledge=knowledgePoint).first()
                    if singleObjectKnowledge:
                        if belongsToPoint == "1":
                            singleObjectKnowledge.match_content = zhishimiaoshu
                            singleObjectKnowledge.save()
                        else:
                            singleObjectKnowledge.delete()
                    else:
                        if belongsToPoint == "1":
                            SingleObjectKnowledge.objects.create(duanzhu_bianhao=bianhao, duanzhu_id=id, match_content=zhishimiaoshu, knowledge=knowledgePoint)

                zsAnnoteate = KnowledgeAnnotate.objects.filter(knowledge_point=knowledgePoint, duanzhu_id=id).first()
                if belongsToPoint == "0":
                    if not zsAnnoteate:
                        KnowledgeAnnotate.objects.create(knowledge_point=knowledgePoint,duanzhu_id=id,duanzhu_bianhao=bianhao,is_belong=belongsToPoint)
                else:
                    if zsAnnoteate:
                        zsAnnoteate.delete()
                success = True
        except Exception as e:
            print(e)
    context["success"] = success

    return JsonResponse(context, safe=False)

@login_required
def saveKnowledgeAnnotate2(request):
    context = {}
    success = False
    user = request.user
    if user:
        try:
            if request.method == 'POST':
                param = json.loads(request.body)
                id = param.get("id")
                bianhao = param.get("bianhao")
                knowledgePoint = param.get("knowledgePoint")
                belongsToPoint = param.get("belongsToPoint")
                zhishimiaoshu = param.get("zhishimiaoshu")
                groups = param.get("groups")
                print(groups)
                if belongsToPoint == "1":
                    if len(groups)>0:
                        for group in groups:
                            char1 = group["char1"]
                            char1Bianhao = group["id1"]
                            char2 = group["char2"]
                            char2Bianhao = group["id2"]
                            relationKnowledge = RelationKnowledge.objects.filter(knowledge=knowledgePoint, duanzhu_bianhao=bianhao, object1_duanzhu_bianhao=char1Bianhao, object2_duanzhu_bianhao=char2Bianhao).first()
                            if not relationKnowledge:
                                RelationKnowledge.objects.create(duanzhu_bianhao=bianhao,object1=char1,object1_duanzhu_bianhao=char1Bianhao,object2=char2,object2_duanzhu_bianhao=char2Bianhao,miaoshu=zhishimiaoshu,knowledge=knowledgePoint,duanzhu_id=id)
                    zsAnnoteate = KnowledgeAnnotate.objects.filter(knowledge_point=knowledgePoint,
                                                                   duanzhu_id=id).first()
                    if zsAnnoteate:
                        zsAnnoteate.delete()
                else:
                    relationKnowledges = list(RelationKnowledge.objects.filter(knowledge=knowledgePoint, duanzhu_bianhao=bianhao))
                    if relationKnowledges:
                        for relationKnowledge in relationKnowledges:
                            relationKnowledge.delete()
                    zsAnnoteate = KnowledgeAnnotate.objects.filter(knowledge_point=knowledgePoint,
                                                                   duanzhu_id=id).first()
                    if not zsAnnoteate:
                        KnowledgeAnnotate.objects.create(knowledge_point=knowledgePoint, duanzhu_id=id,
                                                         duanzhu_bianhao=bianhao, is_belong=belongsToPoint)

                success = True
        except Exception as e:
            print(e)
    context["success"] = success

    return JsonResponse(context, safe=False)

@login_required
def searchZitou(request):
    keywords = request.GET.get('keywords')
    zhishidian = request.GET.get('zhishidian')
    if len(keywords)==1:
        zitous = DuanZhu.objects.filter(zitou=keywords).values_list('id','zitou','duanzhu_bianhao','zhengwen_zhushi')
    else:
        zitous = DuanZhu.objects.filter(zhengwen_zhushi__contains=keywords).values_list('id', 'zitou', 'duanzhu_bianhao', 'zhengwen_zhushi')
    data = [{"id":id,"zitou":zitou,"bianhao":bianhao,"zhengwenzhushi":zhengwenzhushi,"status":None,"miaoshu":None} for id,zitou,bianhao,zhengwenzhushi in zitous]
    for zt in data:
        if zhishidian == "象形":
            xiangxing = Liushu.objects.filter(duanzhu_bianhao=zt["bianhao"],liushu='象形').first()
            if xiangxing:
                zt["status"] = 1
                zt["miaoshu"] = xiangxing.zhishimiaoshu
        elif zhishidian == "指事":
            zhishi = Liushu.objects.filter(duanzhu_bianhao=zt["bianhao"], liushu='指事').first()
            if zhishi:
                zt["status"] = 1
                zt["miaoshu"] = zhishi.zhishimiaoshu
        elif zhishidian == "会意":
            huiyi = Liushu.objects.filter(duanzhu_bianhao=zt["bianhao"], liushu='会意').first()
            if huiyi:
                zt["status"] = 1
                zt["miaoshu"] = huiyi.zhishimiaoshu
        elif zhishidian == "犹":
            you = You.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if you:
                zt["status"] = 1
                zt["miaoshu"] = you.match_content
        elif zhishidian == "构意":
            gouyi = Gouyi.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if gouyi:
                zt["status"] = 1
                zt["miaoshu"] = gouyi.match_content
        elif zhishidian == "随文解之":
            suiwen = Suiwen.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if suiwen:
                zt["status"] = 1
                zt["miaoshu"] = suiwen.match_content
        elif zhishidian == "说字训诂":
            shuozi = Shuozi.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if shuozi:
                zt["status"] = 1
                zt["miaoshu"] = shuozi.match_content
        elif zhishidian == "非是":
            feishi = Feishi.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if feishi:
                zt["status"] = 1
                zt["miaoshu"] = feishi.match_content
        elif zhishidian == "古语":
            guyu = Guyu.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if guyu:
                zt["status"] = 1
                zt["miaoshu"] = guyu.match_content
        elif zhishidian == "声符示源":
            shengfushiyuan = Shengfushiyuan.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if shengfushiyuan:
                zt["status"] = 1
                zt["miaoshu"] = shengfushiyuan.match_content
        elif zhishidian == "联绵词":
            lmc = Lianmianci.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if lmc:
                zt["status"] = 1
                zt["miaoshu"] = lmc.lianmianci
        elif zhishidian == "方言俗语":
            fangsu = Fangsu.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if fangsu:
                zt["status"] = 1
                zt["miaoshu"] = fangsu.match_content
        elif zhishidian == "通语":
            tongyu = Tongyu.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if tongyu:
                zt["status"] = 1
                zt["miaoshu"] = tongyu.match_content
        elif zhishidian == "转语":
            zhuanyu = Zhuanyu.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if zhuanyu:
                zt["status"] = 1
                zt["miaoshu"] = zhuanyu.match_content
        elif zhishidian == "本义":
            benyi = Benyi.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if benyi:
                zt["status"] = 1
                zt["miaoshu"] = benyi.match_content
        elif zhishidian == "别一义":
            bieyiyi = Bieyiyi.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if bieyiyi:
                zt["status"] = 1
                zt["miaoshu"] = bieyiyi.match_content
        elif zhishidian == "古音":
            guyin = Guyin.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if guyin:
                zt["status"] = 1
                zt["miaoshu"] = guyin.match_content
        elif zhishidian == "今音":
            jinyin = Jinyin.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if jinyin:
                zt["status"] = 1
                zt["miaoshu"] = jinyin.match_content
        elif zhishidian == "删":
            shan = Shan.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if shan:
                zt["status"] = 1
                zt["miaoshu"] = shan.match_content
        elif zhishidian == "夺":
            duotuo = Duotuo.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if duotuo:
                zt["status"] = 1
                zt["miaoshu"] = duotuo.match_content
        elif zhishidian == "妄改":
            wanggai = Wanggai.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if wanggai:
                zt["status"] = 1
                zt["miaoshu"] = wanggai.match_content
        elif zhishidian == "正":
            zheng = Zheng.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if zheng:
                zt["status"] = 1
                zt["miaoshu"] = zheng.match_content
        elif zhishidian == "本作":
            benzuo = Benzuo.objects.filter(duanzhu_bianhao=zt["bianhao"]).first()
            if benzuo:
                zt["status"] = 1
                zt["miaoshu"] = benzuo.match_content
        else:
            zt["groups"] = []
            relationKnowledges = list(RelationKnowledge.objects.filter(duanzhu_bianhao=zt["bianhao"],knowledge=zhishidian))
            if relationKnowledges:
                zt["status"] = 1
                if len(relationKnowledges)>0:
                    zt["miaoshu"] = relationKnowledges[0].miaoshu
                for relationKnowledge in relationKnowledges:
                    zt["groups"].append({"char1":relationKnowledge.object1,"id1":relationKnowledge.object1_duanzhu_bianhao,"char2":relationKnowledge.object2,"id2":relationKnowledge.object2_duanzhu_bianhao})

        if zt["status"] != 1:
            zsAnnoteate = KnowledgeAnnotate.objects.filter(knowledge_point=zhishidian, duanzhu_id=zt["id"]).first()
            if zsAnnoteate:
                zt["status"] = zsAnnoteate.is_belong
                zt["miaoshu"] = None
            else:
                zt["status"] = None
                zt["miaoshu"] = None

    return JsonResponse(data, safe=False)

@login_required
def findByZitou(request):
    context = {}
    zitou = request.GET.get('zitou')
    duanzhu = DuanZhu.objects.filter(zitou=zitou).first()
    print(duanzhu)
    if duanzhu:
        context["id"] = duanzhu.id
        context["bianhao"] = duanzhu.duanzhu_bianhao
        context["zitou"] = duanzhu.zitou

    return JsonResponse(context, safe=False)