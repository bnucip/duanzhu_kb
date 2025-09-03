from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Point, MonoRaw, Mono
from django import forms
from django.db import connection
import time

def index(request):
    return render(request, "yubao/index.html")

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

# Simple form for editing script
class MonoRawForm(forms.ModelForm):
    class Meta:
        model = MonoRaw
        fields = ["script"]

def mono_raw_edit(request):
    point = request.GET.get("point")
    char_id = request.GET.get("char_id")
    person = request.GET.get("person")

    print(point, char_id, person)
    mono_raw = get_object_or_404(MonoRaw, point=point, char_id=char_id, person=person)

    form = MonoRawForm(request.POST or None, instance=mono_raw)

    if form.is_valid():
        form.save()

        # Update corresponding Mono record
        try:
            mono = Mono.objects.get(point=mono_raw.point, char_id=mono_raw.char_id)
        except Mono.DoesNotExist:
            mono = None

        if mono:
            parts = mono_raw.script.split(" ")  # assume "C,V,T"
            consonant, vowel, tone = parts[0], " ".join(parts[1:-1]), parts[-1]

            if person == "老男":
                mono.old_consonant = consonant
                mono.old_vowel = vowel
                mono.old_tone = tone
            elif person == "青男":
                mono.young_consonant = consonant
                mono.young_vowel = vowel
                mono.young_tone = tone
            mono.save()

        return redirect("mono_list")

    return render(request, "yubao/mono_raw_edit.html", {
        "form": form,
        "mono_raw": mono_raw,
        "person": person
    })

def rebuild_mono(request):
    """
    Rebuild the mono table from mono_raw, show waiting info and time cost.
    """
    start_time = time.time()

    # Show initial processing page
    if request.GET.get("started") != "1":
        return render(request, "yubao/rebuild_mono_wait.html")

    # Actual rebuilding process
    with connection.cursor() as cur:
        cur.execute("""
            SELECT point, char_id, MIN(char_txt), GROUP_CONCAT(script ORDER BY person)
            FROM yubao_mono_raw
            GROUP BY point, char_id
        """)
        rows_to_insert = []
        for point, char_id, char_txt, scripts in cur.fetchall():
            script_old, script_you = scripts.split(',')
            lst_old = script_old.split()
            lst_you = script_you.split()
            assert len(lst_old) > 2 and len(lst_you) > 2
            rows_to_insert.append([
                point, char_id, char_txt,
                lst_old[0], ' '.join(lst_old[1:-1]), lst_old[-1],
                lst_you[0], ' '.join(lst_you[1:-1]), lst_you[-1]
            ])

        cur.execute("TRUNCATE TABLE yubao_mono")
        cur.executemany("""
            INSERT INTO yubao_mono(
                point,char_id,char_txt,
                old_consonant,old_vowel,old_tone,
                young_consonant,young_vowel,young_tone
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, rows_to_insert)

    time_cost = time.time() - start_time
    return render(request, "yubao/rebuild_mono_done.html", {"time_cost": time_cost})
