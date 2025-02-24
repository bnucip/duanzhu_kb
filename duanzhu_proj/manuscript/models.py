import uuid
from django.db import models

# Create your models here.
class DuanZhu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('编号',max_length=20,null=True,blank=True, unique=True)
    zitou = models.CharField('字头',max_length=20,null=True,blank=True)
    chongwen = models.CharField('重文',max_length=20,null=True,blank=True)
    zhengwen_zhushi = models.TextField('正文注释',null=True,blank=True)
    bushou = models.CharField('部首',max_length=20,null=True,blank=True)
    juan = models.CharField('卷',max_length=20,null=True,blank=True)
    class Meta:
        verbose_name = '段注'
        verbose_name_plural = verbose_name


class SwDu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    du_bianhao = models.CharField('编号',max_length=20,null=True,blank=True)
    zitou = models.CharField('字头',max_length=20,null=True,blank=True)
    zhushi = models.TextField('注释',null=True,blank=True)
    duanzhu_bianhao = models.CharField('段注编号',max_length=20,null=True,blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    class Meta:
        verbose_name = '说文解字读'
        verbose_name_plural = verbose_name


class Xiesheng(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    xieshengzi = models.CharField('谐声字',max_length=20,null=True,blank=True)
    shengfu = models.CharField('声符',max_length=20,null=True,blank=True)
    xieshengzi_duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='谐声字ID', related_name="xieshengzi_duanzhu", null=True)
    shengfu_duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='声符ID', related_name="shengfu_duanzhu", null=True)
    class Meta:
        verbose_name = '谐声声符'
        verbose_name_plural = verbose_name


class Guyunbu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号',max_length=20,null=True,blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    zitou = models.CharField('字头',max_length=20,null=True,blank=True)
    yunbu = models.CharField('韵部',max_length=20,null=True,blank=True)
    yunlei = models.CharField('韵类',max_length=20,null=True,blank=True)
    class Meta:
        verbose_name = '古韵部'
        verbose_name_plural = verbose_name


class Gujinzi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号',max_length=20,null=True,blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    chuxian_zitou = models.CharField('初选字头',max_length=20,null=True,blank=True)
    miaoshu = models.TextField('描述',null=True,blank=True)
    guzi_id = models.CharField('古字ID',max_length=20,null=True,blank=True)
    jinzi_id = models.CharField('今字ID',max_length=20,null=True,blank=True)
    class Meta:
        verbose_name = '古今字'
        verbose_name_plural = verbose_name

class Gouyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    gouyi1 = models.TextField('构意1', null=True, blank=True)
    gouyi2 = models.TextField('构意2', null=True, blank=True)
    gouyi3 = models.TextField('构意3', null=True, blank=True)
    shengfugouyi = models.TextField('声符构意', null=True, blank=True)
    class Meta:
        verbose_name = '构意阐释'
        verbose_name_plural = verbose_name