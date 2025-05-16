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
    img_path = models.CharField('图片路径',max_length=200,null=True,blank=True)
    yema = models.CharField('页码',max_length=200,null=True,blank=True)
    swxz = models.CharField('说文小篆',max_length=20,null=True,blank=True)
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

class Yinyitong(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    object1 = models.TextField('对象1', null=True, blank=True)
    object1_duanzhu_bianhao = models.TextField('对象1段注编号', null=True, blank=True)
    object2 = models.TextField('对象2', null=True, blank=True)
    object2_duanzhu_bianhao = models.TextField('对象2段注编号', null=True, blank=True)
    duanshianyu = models.TextField('段氏按语', null=True, blank=True)
    class Meta:
        verbose_name = '音义同'
        verbose_name_plural = verbose_name

class Zhishimulu(models.Model):
    id = models.IntegerField(primary_key=True)
    tag_name = models.TextField('目录名', null=True, blank=True)
    parent_id = models.IntegerField('父级id', null=True, blank=True)
    level = models.IntegerField('目录层级', null=True, blank=True)
    zhishishuoming = models.TextField('知识说明', null=True, blank=True)
    shuyuxingshi = models.TextField('术语形式', null=True, blank=True)
    yanjiutuijie = models.TextField('研究推介', null=True, blank=True)
    url = models.TextField('请求url', null=True, blank=True)
    class Meta:
        verbose_name = '知识目录'
        verbose_name_plural = verbose_name

class Yinshu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idx = models.CharField('idx', max_length=20, null=True, blank=True)
    book = models.TextField('书名', null=True, blank=True)
    chapter = models.TextField('章节', null=True, blank=True)
    content = models.TextField('原文', null=True, blank=True)
    yiwen = models.TextField('yiwen', null=True, blank=True)
    duanzhu_bianhaos = models.TextField('段注编号', null=True, blank=True)
    class Meta:
        verbose_name = '引书'
        verbose_name_plural = verbose_name

class Liushu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    liushu = models.TextField('六书', null=True, blank=True)
    class Meta:
        verbose_name = '六书'
        verbose_name_plural = verbose_name

class Zhuanzhu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    zhuanzhu = models.TextField('转注', null=True, blank=True)
    class Meta:
        verbose_name = '转注'
        verbose_name_plural = verbose_name

class Jiajie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    jiajiezhuwen = models.TextField('假借注文', null=True, blank=True)
    jiajiebiaoqian = models.TextField('假借标签', null=True, blank=True)
    class Meta:
        verbose_name = '假借'
        verbose_name_plural = verbose_name

class Xingfeizi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    pipeizifuchuan = models.TextField('匹配字符串', null=True, blank=True)
    xingzi = models.TextField('行字', null=True, blank=True)
    feizi = models.TextField('废字', null=True, blank=True)
    class Meta:
        verbose_name = '行废字'
        verbose_name_plural = verbose_name

class Tongzi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    tongzizhuwen = models.TextField('同字注文', null=True, blank=True)
    class Meta:
        verbose_name = '同字'
        verbose_name_plural = verbose_name

class Huxun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    shuojie = models.TextField('说解', null=True, blank=True)
    huxunzu = models.TextField('互训组', null=True, blank=True)
    class Meta:
        verbose_name = '互训'
        verbose_name_plural = verbose_name

class Zhiyan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    zhiyanshuojie = models.TextField('之言说解', null=True, blank=True)
    duixiang = models.TextField('对象', null=True, blank=True)
    class Meta:
        verbose_name = '之言'
        verbose_name_plural = verbose_name

class Lianmianci(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    zitou = models.TextField('字头', null=True, blank=True)
    lianmianci = models.TextField('联绵词', null=True, blank=True)
    ciyileibie = models.TextField('词义类别', null=True, blank=True)
    class Meta:
        verbose_name = '联绵词'
        verbose_name_plural = verbose_name

class Yinshen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    yinshen = models.TextField('引申', null=True, blank=True)
    class Meta:
        verbose_name = '引申义'
        verbose_name_plural = verbose_name

class Benyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    benyi_1 = models.TextField('本义1', null=True, blank=True)
    benyi_2 = models.TextField('本义2', null=True, blank=True)
    class Meta:
        verbose_name = '本义'
        verbose_name_plural = verbose_name

class Gujinyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    shuojie = models.TextField('说解', null=True, blank=True)
    biaoqian = models.TextField('标签', null=True, blank=True)
    class Meta:
        verbose_name = '古义今义'
        verbose_name_plural = verbose_name

class Hunyanxiyan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    duanzhushuyu = models.TextField('段注术语', null=True, blank=True)
    xibianduixiang = models.TextField('辨析对象', null=True, blank=True)
    obj1_duanzhu_id = models.TextField('对象1_duanzhu_id', null=True, blank=True)
    obj2_duanzhu_id = models.TextField('对象2_duanzhu_id', null=True, blank=True)
    obj3_duanzhu_id = models.TextField('对象3_duanzhu_id', null=True, blank=True)
    obj4_duanzhu_id = models.TextField('对象4_duanzhu_id', null=True, blank=True)
    obj5_duanzhu_id = models.TextField('对象5_duanzhu_id', null=True, blank=True)
    class Meta:
        verbose_name = '浑言析言'
        verbose_name_plural = verbose_name

class Ezi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '讹字'
        verbose_name_plural = verbose_name

class Suzi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '俗字'
        verbose_name_plural = verbose_name

class You(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    a = models.TextField('A', null=True, blank=True)
    a_id = models.TextField('A_id', null=True, blank=True)
    b = models.TextField('B', null=True, blank=True)
    b_id = models.TextField('B_id', null=True, blank=True)
    class Meta:
        verbose_name = '犹'
        verbose_name_plural = verbose_name

class Suiwen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '随文'
        verbose_name_plural = verbose_name

class Shuozi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '说字'
        verbose_name_plural = verbose_name

class Feishi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '非是'
        verbose_name_plural = verbose_name

class Fanxun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '反训'
        verbose_name_plural = verbose_name

class Tongxun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '同训'
        verbose_name_plural = verbose_name

class Shuangsheng(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    obj1 = models.TextField('双声对象1', null=True, blank=True)
    obj2 = models.TextField('双声对象2', null=True, blank=True)
    class Meta:
        verbose_name = '双声'
        verbose_name_plural = verbose_name

class Dieyun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '叠韵'
        verbose_name_plural = verbose_name

class Yijinshigu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '以今释古'
        verbose_name_plural = verbose_name

class Hujian(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '互见'
        verbose_name_plural = verbose_name

class Guyu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '古语'
        verbose_name_plural = verbose_name

class Shengfushiyuan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '声符示源'
        verbose_name_plural = verbose_name

class Fangsu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '方言俗语'
        verbose_name_plural = verbose_name

class Tongyu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '通语'
        verbose_name_plural = verbose_name

class Zhuanyu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '转语'
        verbose_name_plural = verbose_name

class Yixiangzu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '义相足'
        verbose_name_plural = verbose_name

class Yintongyiyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '音同义异'
        verbose_name_plural = verbose_name

class Bieyiyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '别一义'
        verbose_name_plural = verbose_name


class Guyin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '古音'
        verbose_name_plural = verbose_name

class Jinyin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '今音'
        verbose_name_plural = verbose_name

class Yinzhuan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '音转'
        verbose_name_plural = verbose_name

class Yinbian(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '音变'
        verbose_name_plural = verbose_name

class Zuijin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '最近'
        verbose_name_plural = verbose_name

class Guheyun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '古合韵'
        verbose_name_plural = verbose_name

class Yiwen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '异文'
        verbose_name_plural = verbose_name

class Shan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '删'
        verbose_name_plural = verbose_name

class Duotuo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content1 = models.TextField('匹配内容1', null=True, blank=True)
    match_content2 = models.TextField('匹配内容2', null=True, blank=True)
    class Meta:
        verbose_name = '夺'
        verbose_name_plural = verbose_name

class Wanggai(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '妄改'
        verbose_name_plural = verbose_name

class Zheng(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '正'
        verbose_name_plural = verbose_name

class Benzuo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    match_content = models.TextField('匹配内容', null=True, blank=True)
    class Meta:
        verbose_name = '本作'
        verbose_name_plural = verbose_name

class Xingfeiyi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duanzhu_bianhao = models.CharField('段注编号', max_length=20, null=True, blank=True)
    duanzhu = models.ForeignKey(DuanZhu, on_delete=models.CASCADE, db_constraint=True, verbose_name='段注ID', null=True)
    yixingyifeishuojie = models.TextField('义行义废说解', null=True, blank=True)
    class Meta:
        verbose_name = '行废义'
        verbose_name_plural = verbose_name
