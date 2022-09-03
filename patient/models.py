from django.db import models
from datetime import datetime
# Create your models here.
class Patient(models.Model):
    patient_id = models.BigAutoField(primary_key=True, verbose_name="病人ID")
    csv_id=models.IntegerField(blank=True, null=True, verbose_name="备用编号")
    name = models.CharField(max_length=20, verbose_name="姓名")
    sex = models.IntegerField(default=0, choices=((1, '男'), (0, '女')), verbose_name="性别")
    age = models.IntegerField(verbose_name="年龄")
    weight=models.FloatField(blank=True, null=True, verbose_name="体重")
    diagnose=models.CharField(blank=True, null=True, max_length=50, verbose_name="诊断")
    operation=models.CharField(blank=True, null=True, max_length=50, verbose_name="手术")
    ventilation_mode=models.IntegerField(blank=True, null=True,default=0, choices=((0, '喉罩'), (1, '气管插管')), verbose_name="通气方式")
    nerve_block=models.IntegerField(blank=True, null=True,default=0, choices=((0, '无'), (1, '有')), verbose_name="神经阻滞")
    analgesic_pump=models.IntegerField(blank=True, null=True,default=0, choices=((0, '无'), (1, '有')), verbose_name="镇痛泵")
    add_time = models.DateTimeField(default=datetime.now,verbose_name='添加时间')
    sample_num=models.IntegerField(default=0,verbose_name="样本数")
    

    class Meta:
        verbose_name = '病人'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.patient_id)+'_'+self.name

class Sample(models.Model):
    sample_id = models.BigAutoField(primary_key=True, verbose_name="样本ID")
    patient_id = models.ForeignKey(Patient, verbose_name="病人ID", on_delete=models.CASCADE,related_name="patient_sample")
    heart_rate = models.IntegerField(blank=True, null=True, verbose_name="心率")
    diastolic_pressure = models.IntegerField(blank=True, null=True, verbose_name="舒张压")
    systolic_pressure = models.IntegerField(blank=True, null=True, verbose_name="收缩压")
    before_operation=models.IntegerField(blank=True, null=True,default=0, choices=((0,'术前'), (1,'术后')), verbose_name="术前术后")
    video = models.FileField(verbose_name='视频', upload_to='mp4/')
    biology=models.FileField(blank=True, null=True,verbose_name="生理信号", upload_to='csv/')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '样本'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.sample_id)+'_'+str(self.patient_id)

class User(models.Model):
    user_id=models.BigAutoField(primary_key=True, verbose_name="用户ID")
    account=models.CharField(max_length=20, verbose_name="账号")
    password=models.CharField(max_length=100, verbose_name="密码")
    name=models.CharField(max_length=20, verbose_name="昵称")

    def __str__(self):
        return str(self.user_id)

class Score(models.Model):
    user_id = models.ForeignKey(User, verbose_name="用户ID", on_delete=models.CASCADE,related_name="score_user")
    sample_id = models.ForeignKey(Sample, verbose_name="样本ID", on_delete=models.CASCADE,related_name="score_sample")
    sum_score=models.FloatField(blank=True, null=True, verbose_name="总分")
    FLACC_score=models.FloatField(blank=True, null=True, verbose_name="FLACC")
    FACE_score=models.FloatField(blank=True, null=True, verbose_name="FACE")
    legs_score=models.FloatField(blank=True, null=True, verbose_name="legs")
    Acitivity_score=models.FloatField(blank=True, null=True, verbose_name="Acitivity")
    Cry_score=models.FloatField(blank=True, null=True, verbose_name="Cry")
    consolability_score=models.FloatField(blank=True, null=True, verbose_name="consolability")
    VAS_score=models.FloatField(blank=True, null=True, verbose_name="VAS")
    lianpu_score=models.FloatField(blank=True, null=True, verbose_name="脸谱")
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    def __str__(self):
        return str(self.user_id)+'_'+str(self.sample_id)

class AIScore(models.Model):
    sample_id = models.ForeignKey(Sample, verbose_name="样本ID", on_delete=models.CASCADE,related_name="AIscore_sample")
    
    face_score_npy_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="面部帧评分")
    voice_score_npy_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="声音帧评分")
    body_score_npy_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="肢体帧评分")

    face_score=models.FloatField(blank=True, null=True, verbose_name="面部评分")
    voice_score=models.FloatField(blank=True, null=True, verbose_name="声音评分")
    body_score=models.FloatField(blank=True, null=True, verbose_name="肢体评分")
    bio_score=models.FloatField(blank=True, null=True, verbose_name="生理评分")
    all_score=models.FloatField(blank=True, null=True, verbose_name="总评分")

    face_mp4_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="面部特征视频")
    voice_npy_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="声音特征视频")
    body_mp4_path = models.CharField(blank=True, null=True,max_length=100, verbose_name="肢体特征视频")

    def __str__(self):
        return str(self.sample_id)