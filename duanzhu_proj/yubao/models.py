from django.db import models

class Point(models.Model):
    id = models.AutoField(primary_key=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    firstLevelid = models.CharField(max_length=20, unique=True, null=True, blank=True)
    filepath = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    village = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=1500, null=True, blank=True)
    population = models.CharField(max_length=255, null=True, blank=True)
    nation = models.TextField(null=True, blank=True)
    minorityInfo = models.TextField(null=True, blank=True)
    dialectInfo = models.TextField(null=True, blank=True)
    operaInfo = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    degree = models.CharField(max_length=50, null=True, blank=True)
    area = models.CharField(max_length=50, null=True, blank=True)
    slice = models.CharField(max_length=50, null=True, blank=True)
    slices = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "yubao_point"


class MonoRaw(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.CharField(max_length=20, null=True, blank=True)
    char_id = models.CharField(max_length=4, null=True, blank=True)
    char_txt = models.CharField(max_length=4, null=True, blank=True)
    person = models.CharField(max_length=20, null=True, blank=True)
    script = models.CharField(max_length=200, null=True, blank=True)
    script_bk = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "yubao_mono_raw"
        indexes = [
            models.Index(fields=["point", "char_id"], name="idx_mono_raw_point_char"),
        ]

class Mono(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.CharField(max_length=20, null=True, blank=True)
    char_id = models.CharField(max_length=4, null=True, blank=True)
    char_txt = models.CharField(max_length=4, null=True, blank=True)
    old_consonant = models.CharField(max_length=20, null=True, blank=True)
    old_vowel = models.CharField(max_length=20, null=True, blank=True)
    old_tone = models.CharField(max_length=20, null=True, blank=True)
    young_consonant = models.CharField(max_length=20, null=True, blank=True)
    young_vowel = models.CharField(max_length=20, null=True, blank=True)
    young_tone = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "yubao_mono"
        constraints = [
            models.UniqueConstraint(fields=["point", "char_id"], name="uniq_mono_point_char"),
        ]