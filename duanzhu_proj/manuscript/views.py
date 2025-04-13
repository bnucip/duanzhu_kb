from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from .models import DuanZhu, SwDu, Gujinzi, Guyunbu, Gouyi, Yinyitong, Yinshu, Zhishimulu, Liushu, Zhuanzhu, Jiajie, \
    Tongzi, Xingfeizi, Huxun, Zhiyan, Lianmianci, Yinshen, Benyi, Gujinyi, Hunyanxiyan, Ezi, Suzi, Suiwen, You, Shuozi, \
    Feishi, Fanxun, Tongxun, Shuangsheng, Dieyun, Yijinshigu, Hujian, Guyu, Shengfushiyuan, Fangsu, Tongyu, Zhuanyu, \
    Yixiangzu, Yintongyiyi, Bieyiyi, Guyin, Jinyin, Yinzhuan, Yinbian, Zuijin, Guheyun, Yiwen, Shan, Duotuo, Wanggai, \
    Zheng, Benzuo
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
        else:
            data = Zhishimulu.objects
            data = data.filter(shuyuxingshi__contains=keyword)
            paginator = Paginator(data,10)
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
        if p.match_content1:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content1, '<span>' + p.match_content1 + '</span>')
        if p.match_content2:
            duanzhu.zhengwen_zhushi = duanzhu.zhengwen_zhushi.replace(p.match_content2, '<span>' + p.match_content2 + '</span>')
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