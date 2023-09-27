import functools
from django.shortcuts import render,redirect
from patient.models import *
from patient.apps import ai,lock
from django.core import serializers
import json
import datetime
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,FileResponse
from django.db.models import F,Count
from django.db import IntegrityError
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import make_password,check_password
import re
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
# from ai import ai_main
from django.conf import settings
import threading
import numpy as np
import csv
from datetime import datetime
import pandas as pd
from django.db.models import Avg
import time
from django.db.models.functions import Abs
from django.core.cache import cache
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error

#修改3：引入math库
import math
#修改3结束

# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
# from .tasks import analyze_video
from django.core.files.storage import default_storage

class myThread(threading.Thread):
    def __init__(self, sampleID,videopath):
        threading.Thread.__init__(self)
        self.sampleID=sampleID
        self.videopath=videopath

    def run(self):
        print("thread start!!")
        lock.acquire()
        try:
            # hrt=HRThread(self.videopath)
            # hrt.start()
            print(self.videopath)
            all_score,face_score,voice_score=ai.predict(self.videopath)
            # hrt.join()
            aiscores=AIScore.objects.filter(sample_id_id=self.sampleID)
            for aiscore in aiscores:
                aiscore.delete()
            AIScore.objects.update_or_create(sample_id_id=self.sampleID,all_score=all_score,face_score=face_score,voice_score=voice_score)
            # ,heart_rate=hrt.heart_rate,diastolic_pressure=hrt.diastolic_pressure,systolic_pressure=hrt.systolic_pressure)
            cache.clear()
        except Exception as e:
            print("评分失败！原因："+str(e.args))
        lock.release()
        # face_score,face_mp4_path,face_score_npy_path,voice_score,voice_score_npy_path=ai_main(self.videopath)
        
        print("thread done!!")

class HRThread(threading.Thread):
    def __init__(self, videopath):
        threading.Thread.__init__(self)
        self.videopath=videopath
        self.heart_rate=None
        self.diastolic_pressure=None
        self.systolic_pressure=None

    def run(self):
        print("HR thread start!!")
        try:
            BVP_signal,hr,h_bp,l_bp=ai.BVP_pred.predict(self.videopath)
            self.heart_rate=hr
            self.diastolic_pressure=h_bp
            self.systolic_pressure=l_bp
        except Exception as e:
            print("心率血压预测失败！原因："+str(e.args))
        print("HR thread done!!")

def cache_get(key:str,exe:str,filter_value=None):
    res=cache.get(key)
    if res is None:
        res = eval(exe)
        cache.set(key, res)
    return res

# Create your views here.
def login(request):
    user = checkLoginStatus(request)
    if user!='':
        return redirect('/index')
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def index(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    msg=request.session['msg']
    return render(request, 'index.html',{"currentuser":user,"msg":msg})

def checkLoginStatus(request):
    if 'account' in request.session and request.session['account']:
        account = request.session['account']
        checkIsLogin(request)
        user = User.objects.filter(account=account)[0]
        return user
    return ''

def postregister(request):
    if request.method == 'POST':
        password = request.POST['pwd']
        pwd2=request.POST['pwd2']
        name = request.POST['name']
        phoneNum = request.POST['phoneNum']
        # verifyCode = request.POST['verifyCode']
        if pwd2!=password:
            msg="两次密码输入不一致！"
            return render(request, 'register.html',{"msg":msg})
        res = User.objects.filter(account=phoneNum)
        if len(res)>0:
            msg="该账号已存在！"
            return render(request, 'register.html',{"msg":msg})
        # m = hashlib.md5()
        # m.update(password.encode('utf-8'))
        password = make_password(password, 'sha', 'pbkdf2_sha256')
        
        User.objects.create(account=phoneNum,password=password,name=name,usrtype=1)
        
        request.session['addData_flag'] = False
        request.session['addData_name'] = ""
        request.session['account'] = phoneNum
        request.session['name'] = name
        request.session["msg"]="注册账号 "+phoneNum+" 成功！"
        return redirect('/index')

        # request.session['member_id'] = res.id
        # request.session['username'] = res.username
        # checkIsLogin(request)
        return HttpResponse("注册成功")

    else:
        
        return render(request, 'register.html')

def addData(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    flag=request.session['addData_flag']
    name=request.session['addData_name']
    msg=request.session['msg']
    request.session['addData_flag'] = False
    request.session['addData_name'] = ""
    request.session['msg'] = ""
    if request.method == "POST":
        name=request.POST.get("name")
        order=request.POST.get("order")
        page=request.POST.get("page")
        page=int(page)-1
        page_size=10
        res=Patient.objects.filter(name__contains=name).order_by('-add_time')
        total=len(res)
        if order=="reverse":
            res=res.reverse()
        res=res[page*page_size:(page+1)*page_size]
        patient_list=[]
        for patient in res:
            row={}
            row['csv_id']=patient.csv_id
            row['pk']=patient.pk
            row['name']=patient.name
            row['sex']=patient.get_sex_display()
            row['age']=patient.age
            row['add_time']=patient.add_time.strftime('%Y-%m-%d %H:%M:%S')
            row['sample_num']=patient.patient_sample.count()
            patient_list.append(row)
        json_return={'patient_list':patient_list,'total':total}
        json_data=json.dumps(json_return, ensure_ascii=False)
        print("search"+name)
        return HttpResponse(json_data,content_type='application/json')
    return render(request, 'addData.html',{"currentuser":user,"flag":flag,"name":name,"msg":msg})

def addPatientSuccess(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method=="POST":
        values={}
        name=request.POST.get("name")
        for key in Patient.objects.values().first().keys():
            value=""
            if key=="patient_id" or key=="add_time":
                continue
            else:
                value=request.POST.get(key)
            if value=="":
                value=None
            if value is not None:
                if key in ["csv_id","sex","age","ventilation_mode","nerve_block","analgesic_pump"]:
                    value=int(float(value)) 
                if key=="weight":
                    value=float(value) 
            values[key]=value
        print(values)
        Patient.objects.create(**values)
        cache.clear()
        request.session['addData_flag'] = True
        request.session['addData_name'] = name
        request.session['msg'] = "添加病人 "+name+" 成功！"
        return redirect('/addData')
        #return HttpResponse(str,content_type='text/plain;charset=utf-8')
            
        
    #return render(request, 'addData.html')

def addPatientDataSuccess(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    account=request.session["account"]
    user = User.objects.filter(account=account)[0]
    if request.method=="POST":
        values={}
        for key in Sample.objects.values().first().keys():
            value=""
            if key=="sample_id" or key=="add_time":
                continue
            if key=="video" or key=="biology":
                if key in request.FILES.keys():
                    value=request.FILES[key]
            else:
                value=request.POST.get(key)
            if value=="":
                value=None
            if key=="patient_id_id":
                value=int(value.split(':')[1])
            values[key]=value
        
        print(values)
        sample=Sample.objects.create(**values)
        cache.clear()
        sampleID=sample.pk

        t=myThread(sampleID,os.path.join(settings.MEDIA_ROOT,sample.video.path))
        t.start()
        # return HttpResponse(str,content_type='text/plain;charset=utf-8')
        request.session['addData_flag'] = False
        request.session['addData_name'] = ""
        request.session['msg'] = "添加样本成功！"
        return redirect("/sampleDetail/"+str(sampleID))

def postlogin(request):
    if request.method == "POST":
        userName = request.POST.get('account')
        userPassword=request.POST.get('password')
        res1 = User.objects.filter(account=userName)
        msg="账号不存在！"
        if not res1:
            return render(request, 'login.html',{"msg":msg})

        else:
            res = res1[0]
            # m = hashlib.md5()
            # m.update(userPassword.encode('utf-8'))
            # userPassword = m.hexdigest()
            # if res.password == userPassword:
            if check_password(userPassword, res.password):
                # if res.account=='sue&hzo':
                #     return redirect('/mia')
                request.session['addData_flag'] = False
                request.session['addData_name'] = ""
                request.session['account'] = res.account
                request.session['name'] = res.name
                request.session["msg"]=""
                checkIsLogin(request)
                return redirect('/index')
            else:
                msg="用户名或密码错误！"
                return render(request, 'login.html',{"msg":msg})
                
    else:
        return redirect("/")

def checkIsLogin(request):
    if not request.session.session_key:
        request.session.set_expiry(0)
        request.session.create()
    key = request.session.session_key
    date = Session.objects.filter(session_key=key)[0].session_data
    Session.objects.filter(session_data=date).exclude(session_key=key).delete()


def logout(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/login')
    try:
        del request.session['account']
        del request.session['name']
        request.session.flush()
        print("注销成功")
        return redirect("/")
    except KeyError:
        print("del session failed...")
        return redirect("/")

def dataList(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        account=request.POST.get("account")

        name1=request.POST.get("name1")
        order1=request.POST.get("order1")
        page1=request.POST.get("page1")
        page1=int(page1)-1

        name2=request.POST.get("name2")
        order2=request.POST.get("order2")
        page2=request.POST.get("page2")
        page2=int(page2)-1

        page_size=10

        all_sample=cache_get('all_sample','Sample.objects.all()')
        user = User.objects.filter(account=account)[0]
        user_score=cache_get('user_score_'+str(user.account),'filter_value.score_user.all()',user)
        tmp=[]
        for sample in all_sample:
            tmp.append(sample.pk)
        all_sample=tmp.copy()
        user_sample=[]
        # user_sample=list(all_sample.none())
        for score in user_score:
            user_sample.append(score.sample_id_id)

        rest_sample=[]
        for sample in all_sample:
            if sample not in user_sample:
                rest_sample.append(sample)
        
        rest_patient=[]
        user_patient=[]
        tmp=cache_get('rest_patient_'+name1,'Patient.objects.filter(name__contains=filter_value)',name1)
        for patient in tmp:
            rest_patient.append(patient.pk)
        tmp=cache_get('user_patient_'+name2,'Patient.objects.filter(name__contains=filter_value)',name2)
        for patient in tmp:
            user_patient.append(patient.pk)

        rest_sample=cache_get('rest_sample_'+str(user.account),'Sample.objects.filter(pk__in=filter_value).order_by("-add_time")',rest_sample)
        user_sample=Score.objects.filter(sample_id_id__in=user_sample,user_id_id=user.pk).order_by('-add_time')

        tmp=[]
        for sample in rest_sample:
            if sample.patient_id_id in rest_patient:
                tmp.append(sample)
        rest_sample=tmp.copy()
        tmp=[]
        for score in user_sample:
            sample=Sample.objects.get(pk=score.sample_id_id)
            if sample.patient_id_id in user_patient:
                tmp.append(sample)
        user_sample=tmp.copy()

        total1=len(rest_sample)
        total2=len(user_sample)

        if order1=="reverse":
            rest_sample.reverse()
        if order2=="reverse":
            user_sample.reverse()

        lianpu_list=['','A','B','C','D','E','F']
        
        rest_list=[]
        for rest in rest_sample[page1*page_size:(page1+1)*page_size]:
            row={}
            patient=cache_get('patient_'+str(rest.patient_id_id),'Patient.objects.get(pk=filter_value)',rest.patient_id_id)
            row["patient_id"]=patient.csv_id
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["sex"]=patient.get_sex_display()
            row["age"]=patient.age
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            row["add_time"]=rest.add_time.strftime('%Y-%m-%d %H:%M:%S')
            rest_list.append(row)

        user_list=[]
        for rest in user_sample[page2*page_size:(page2+1)*page_size]:
            row={}
            score=Score.objects.get(sample_id_id=rest.pk,user_id_id=user.pk)
            ai_score=cache_get('ai_score_'+str(rest.pk),'AIScore.objects.filter(sample_id_id=filter_value)',rest.pk)
            patient=cache_get('patient_'+str(rest.patient_id_id),'Patient.objects.get(pk=filter_value)',rest.patient_id_id)
            row["patient_id"]=patient.csv_id
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            row["sum"]=score.sum_score
            row["FLACC"]=score.FLACC_score
            row["all_score"]=round(ai_score[0].all_score*10,2) if len(ai_score)>0 else '空'
            row["face_score"]=round(ai_score[0].face_score*10,2) if len(ai_score)>0 else '空'
            row["voice_score"]=round(ai_score[0].voice_score*10,2) if len(ai_score)>0 else '空'
            # row["VAS"]=score.VAS_score
            # row["lianpu"]=lianpu_list[int(score.lianpu_score)] if score.lianpu_score is not None else None
            row["add_time"]=score.add_time.strftime('%Y-%m-%d %H:%M:%S')
            user_list.append(row)
            
        output={"rest_list":rest_list,"done_list":user_list}
        for k,v in output.items():
            for i in range(len(v)):
                for kk,vv in v[i].items():
                    if vv==None:
                        output[k][i][kk]='空'
        output["total1"]=total1
        output["total2"]=total2

        json_data=json.dumps(output, ensure_ascii=False)

        return HttpResponse(json_data,content_type='application/json')
        
    else:
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        msg=request.session['msg']
        request.session['msg']=""
        return render(request, 'dataList.html',{"currentuser":user,"msg":msg})

def export_excel(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        account=request.POST.get("account")

        name1=request.POST.get("name1")
        order1=request.POST.get("order1")

        name2=request.POST.get("name2")
        order2=request.POST.get("order2")

        all_sample=Sample.objects.all()
        all_score=Score.objects.all()
        print("export_excel",name1,name2,order1,order2)

        tmp=[]
        for sample in all_sample:
            tmp.append(sample.pk)
        all_sample=tmp.copy()
        user_sample=[]
        for score in all_score:
            user_sample.append(score.sample_id_id)
        user_sample=list(set(user_sample))

        rest_sample=[]
        for sample in all_sample:
            if sample not in user_sample:
                rest_sample.append(sample)
        
        rest_patient=[]
        user_patient=[]
        for patient in Patient.objects.filter(name__contains=name1):
            rest_patient.append(patient.pk)
        for patient in Patient.objects.filter(name__contains=name2):
            user_patient.append(patient.pk)

        rest_sample=Sample.objects.filter(pk__in=rest_sample).order_by('-add_time')
        user_sample=Sample.objects.filter(pk__in=user_sample).order_by('-add_time')

        tmp=[]
        for sample in rest_sample:
            if sample.patient_id_id in rest_patient:
                tmp.append(sample)
        rest_sample=tmp.copy()
        tmp=[]
        for sample in user_sample:
            if sample.patient_id_id in user_patient:
                tmp.append(sample)
        user_sample=tmp.copy()

        if order1=="reverse":
            rest_sample.reverse()
        if order2=="reverse":
            user_sample.reverse()

        # lianpu_list=['','A','B','C','D','E','F']
        # Create the HttpResponse object with the appropriate CSV header.
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="scoreList.csv"'
        # with open('/hdd/sdb1/lzq/PAIN/media/scoreList.csv','w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['姓名', '性别', '年龄', '视频', '生理', 'FLACCs', 'FLACCs', 'FLACCs', 'FLACCs', 'FLACCs', '疼痛总分s', '疼痛总分s', '疼痛总分s', '疼痛总分s', '疼痛总分s', 'AI脸', 'AI声', 'AI脸+声'])

        #     for rest in user_sample:
        #         row = []
        #         scores = Score.objects.filter(sample_id_id=rest.pk)
        #         ai_scores = AIScore.objects.filter(sample_id_id=rest.pk)
        #         patient = Patient.objects.get(pk=rest.patient_id_id)

        #         row.extend([patient.name, patient.get_sex_display(), patient.age])
        #         row.append(rest.video.name.split('/')[-1])
        #         row.append(rest.biology.name.split('/')[-1] if rest.biology else '')

        #         for score in scores:
        #             row.append(score.FLACC_score)
        #         row.extend(['' for _ in range(5 - len(scores))])

        #         for score in scores:
        #             row.append(score.sum_score)
        #         row.extend(['' for _ in range(5 - len(scores))])

        #         if ai_scores:
        #             row.extend([ai_scores[0].face_score, ai_scores[0].voice_score, ai_scores[0].all_score])

        #         writer.writerow(row)
        file = open('/hdd/sdb1/lzq/PAIN/media/scoreList.csv', 'rb')
        response = FileResponse(file, as_attachment=True)
        return response
        import xlwt
        from io import BytesIO
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=scoreList.xls'
        user_list=[]
        ws = xlwt.Workbook(encoding='utf-8')
        w = ws.add_sheet('sheet1')
        w.write(0, 0, u'姓名')
        w.write(0, 1, u'性别')
        w.write(0, 2, u'年龄')
        w.write(0, 3, u'视频')
        w.write(0, 4, u'生理')
        w.write(0, 5, u'FLACCs')
        w.write(0, 10, u'疼痛总分s')
        w.write(0, 15, u'AI脸')
        w.write(0, 16, u'AI声')
        w.write(0, 17, u'AI脸+声')
        excel_row = 1
        for rest in user_sample:
            row={}
            scores=Score.objects.filter(sample_id_id=rest.pk)
            ai_scores=AIScore.objects.filter(sample_id_id=rest.pk)
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["name"]=patient.name
            row["sex"]=patient.get_sex_display() 
            row["age"]=patient.age
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else ''
            for i,v in enumerate(row.values()):
                # print(v)
                w.write(excel_row, i, v)
            
            for i,score in enumerate(scores):
                w.write(excel_row, i+5,score.FLACC_score)
                w.write(excel_row, i+10,score.sum_score)
                # print(score.FLACC_score)
            if len(ai_scores)>0:
                w.write(excel_row, 15, ai_scores[0].face_score)
                w.write(excel_row, 16, ai_scores[0].voice_score)
                w.write(excel_row, 17, ai_scores[0].all_score)

            excel_row+=1
        # 写出到IO
        output = BytesIO()
        ws.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response
        

def scoreList(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        time1=time.time()
        account=request.POST.get("account")

        name1=request.POST.get("name1")
        order1=request.POST.get("order1")
        page1=request.POST.get("page1")
        page1=int(page1)-1

        name2=request.POST.get("name2")
        order2=request.POST.get("order2")
        page2=request.POST.get("page2")
        page2=int(page2)-1

        page_size=10

        all_sample=cache_get('all_sample','Sample.objects.all()')
        all_score=cache_get('all_score','Score.objects.all()')
       
        tmp=[]
        for sample in all_sample:
            tmp.append(sample.pk) # 添加每一个sample的主键（primary_key）
        all_sample=tmp.copy()
        user_sample=[]
        for score in all_score:
            user_sample.append(score.sample_id_id)
        user_sample=list(set(user_sample)) # 去除重复的score中的sample_id
        

        rest_sample=[]
        for sample in all_sample:
            if sample not in user_sample:
                rest_sample.append(sample)  # 将不在score中的sample记录下来，也就是记录未打分的sample
        
        rest_patient=[]
        user_patient=[]
        
        tmp=cache_get('rest_patient_'+name1,'Patient.objects.filter(name__contains=filter_value)',name1)
        for patient in tmp:
            rest_patient.append(patient.pk)  # 根据name1添加Patient主键
        tmp=cache_get('user_patient_'+name2,'Patient.objects.filter(name__contains=filter_value)',name2)
        for patient in tmp:
            user_patient.append(patient.pk)  # 根据name2添加Patient主键

        rest_sample=cache_get('rest_sample','Sample.objects.filter(pk__in=filter_value).order_by("-add_time")',rest_sample)
        # 根据rest_sample的主键，query其他数据出来
        user_sample=cache_get('user_sample','Sample.objects.filter(pk__in=filter_value).order_by("-add_time")',user_sample)
        # 根据user_sample的主键，query其他数据出来

        tmp=[]
        for sample in rest_sample:
            if sample.patient_id_id in rest_patient:
                tmp.append(sample)
        rest_sample=tmp.copy()
        tmp=[]
        for sample in user_sample:
            if sample.patient_id_id in user_patient:
                tmp.append(sample)
        user_sample=tmp.copy()

        total1=len(rest_sample)
        total2=len(user_sample)

        if order1=="reverse":
            rest_sample.reverse()
        if order2=="reverse":
            user_sample.reverse()

        lianpu_list=['','A','B','C','D','E','F']
        
        rest_list=[]
        for rest in rest_sample[page1*page_size:(page1+1)*page_size]:
            row={}
            patient=cache_get('patient_'+str(rest.patient_id_id),'Patient.objects.get(pk=filter_value)',rest.patient_id_id)
            row["patient_id"]=patient.csv_id
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["sex"]=patient.get_sex_display()
            row["age"]=patient.age
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            row["add_time"]=rest.add_time.strftime('%Y-%m-%d %H:%M:%S')
            rest_list.append(row)

        user_list=[]
        for rest in user_sample[page2*page_size:(page2+1)*page_size]:
            row={}
            scores=cache_get('scores_'+str(rest.pk),'Score.objects.filter(sample_id_id=filter_value)',rest.pk)
            ai_score=cache_get('ai_score_'+str(rest.pk),'AIScore.objects.filter(sample_id_id=filter_value)',rest.pk)
            patient=cache_get('patient_'+str(rest.patient_id_id),'Patient.objects.get(pk=filter_value)',rest.patient_id_id)
            row["patient_id"]=patient.csv_id
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            sum_tmp=scores.aggregate(Avg("sum_score"))["sum_score__avg"]  # aggregate函数是一个query方法，里面可以添加sql语句的统计函数
            row["sum"]=round(sum_tmp,2) if sum_tmp is not None else None
            FLACC_tmp=scores.aggregate(Avg("FLACC_score"))["FLACC_score__avg"] 
            row["FLACC"]=round(FLACC_tmp,2) if FLACC_tmp is not None else None
            row["all_score"]=round(ai_score[0].all_score*10,2) if len(ai_score)>0 else '空'
            row["face_score"]=round(ai_score[0].face_score*10,2) if len(ai_score)>0 else '空'
            row["voice_score"]=round(ai_score[0].voice_score*10,2) if len(ai_score)>0 else '空'
            # row["VAS"]=round(scores.aggregate(Avg("VAS_score"))["VAS_score__avg"],2)
            # row["lianpu"]=lianpu_list[int(scores.aggregate(Avg("lianpu_score"))["lianpu_score__avg"])] if scores.aggregate(Avg("lianpu_score"))["lianpu_score__avg"] else None
            row["score_num"]=len(scores)
            scoreDicList=[]
            
            for score in scores:
                scoreDic={}
                user=User.objects.get(pk=score.user_id_id)
                scoreDic["name"]=user.name
                scoreDic["sum"]=score.sum_score
                scoreDic["FLACC"]=score.FLACC_score
                # scoreDic["VAS"]=score.VAS_score
                # scoreDic["lianpu"]=lianpu_list[int(score.lianpu_score)] if score.lianpu_score else None
                scoreDic["add_time"]=score.add_time.strftime('%Y-%m-%d %H:%M:%S')
                scoreDicList.append(scoreDic)
            for i in range(len(scoreDicList)):
                for kk,vv in scoreDicList[i].items():
                    if vv==None:
                        scoreDicList[i][kk]='空'
            row["scoreDicList"]=scoreDicList
            user_list.append(row)
        
        # 计算所有sample平均FLACC_score
        # FLACC_score_all=[]
        # for item in all_user_sample:
        #     scores=Score.objects.filter(sample_id_id=item.pk)
        #     FLACC_tmp=scores.aggregate(Avg("FLACC_score"))["FLACC_score__avg"]
        #     FLACC_score_all.append(round(FLACC_tmp,2) if FLACC_tmp is not None else None)
        # print("FLACC_score_all")
        # print(len(FLACC_score_all))
        # print(FLACC_score_all)

        # # 分箱统计
        # flacc_max=max(FLACC_score_all)
        # print(flacc_max)
        # hist_data = [0] * 11 
        # for score in FLACC_score_all:
        #     # index = min(int(score/5), 9)
        #     hist_data[int(score)] += 1
        # # 获取所有平均flacc分数完毕


        output={"rest_list":rest_list,"done_list":user_list}
        for k,v in output.items():
            for i in range(len(v)):
                for kk,vv in v[i].items():
                    if vv==None:
                        output[k][i][kk]='空'
        output["total1"]=total1
        output["total2"]=total2
      
       

        json_data=json.dumps(output, ensure_ascii=False)

        time2=time.time()

        print(f'Time taken: {time2 - time1:.6f} seconds')
        return HttpResponse(json_data,content_type='application/json')
        
    else:
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        msg=request.session['msg']
        request.session['msg']=""
        return render(request, 'scoreList.html',{"currentuser":user,"msg":msg})

def calculate_metrics(list1, list2):

    # Ensure the lists are numpy arrays
    list1, list2 = np.array(list1), np.array(list2)

    # Calculate MAE
    mae = mean_absolute_error(list1, list2)

    # Calculate PCC
    pcc = pearsonr(list1, list2)[0]

    # Calculate CCC
    mean_list1, mean_list2 = np.mean(list1), np.mean(list2)
    var_list1, var_list2 = np.var(list1), np.var(list2)
    cov = np.cov(list1, list2)[0][1]
    ccc = (2 * cov) / (var_list1 + var_list2 + (mean_list1 - mean_list2) ** 2)

    return mae, pcc, ccc

def getFlaccCount(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        #1.获取request请求传回的参数
        account = request.POST.get("account")
        isAll = request.POST.get("isAll")
        flacc_startDate = request.POST.get("flacc_startDate")
        flacc_endDate = request.POST.get("flacc_endDate")
        print(flacc_startDate,flacc_endDate)

        if isAll=="true" or (flacc_startDate=="" and flacc_endDate==""):      #如果不指定时间区间，则默认计算所有已打分样本的MAE：
            scores = Score.objects.filter(FLACC_score__isnull=False)  # 获取所有样本的评分
            patients = Patient.objects.annotate(sample_count=Count('patient_sample')).filter(sample_count__gt=0, age__isnull=False)
        else:
            if flacc_startDate=="":
                flacc_startDate = datetime.now() - timedelta(weeks=5000)
            elif flacc_endDate=="":
                flacc_endDate = datetime.now() + timedelta(weeks=1)
            scores = Score.objects.filter(add_time__range=(flacc_startDate, flacc_endDate), FLACC_score__isnull=False)
            patients = Patient.objects.annotate(sample_count=Count('patient_sample')).filter(add_time__range=(flacc_startDate, flacc_endDate), sample_count__gt=0, age__isnull=False)
            # patients = Patient.objects.filter(add_time__range=(flacc_startDate, flacc_endDate), age__isnull=False)
        
        user_sample=[]
        for score in scores:
            user_sample.append(score.sample_id_id)
        user_sample=list(set(user_sample)) # 去除重复的score中的sample_id
        user_sample=Sample.objects.filter(pk__in=user_sample).order_by('-add_time') 
        all_user_sample=list(user_sample).copy()
         # 计算所有sample平均FLACC_score
        FLACC_score_all=[]
        AI_score_all=[]
        for item in all_user_sample:
            FLACC_scores=Score.objects.filter(sample_id_id=item.pk)
            ai_scores=AIScore.objects.filter(sample_id_id=item.pk)
            if len(FLACC_scores)==0 or len(ai_scores)==0:
                continue
            FLACC_tmp=FLACC_scores.aggregate(Avg("FLACC_score"))["FLACC_score__avg"]
            AI_tmp=ai_scores[0].all_score
            FLACC_score_all.append(round(FLACC_tmp,2))
            AI_score_all.append(round(AI_tmp,2))

        hist_data = [0] * 11 
        for score in FLACC_score_all:
            hist_data[int(score)] += 1
            
        mae,pcc,ccc=calculate_metrics(FLACC_score_all,AI_score_all)

        #返回MAE值的计算结果
        # output = {"MAE(FLACC,AI_total)":mae}
        hist_data_age = [0] * 18 
        for item in patients:
            hist_data_age[int(item.age)] += 1
        #返回统计好的数据结果
        print(mae,pcc,ccc,hist_data,hist_data_age)
        output = {"hist_data":hist_data,"stats":[mae,pcc,ccc],"hist_data_age":hist_data_age}
        json_data = json.dumps(output, ensure_ascii=False)

        return HttpResponse(json_data, content_type='application/json')

    else:     #如果不是POST请求
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        msg=request.session['msg']
        request.session['msg']=""
        return render(request, 'scoreList.html',{"currentuser":user,"msg":msg})


def deleteSample(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]

        sampleID=request.POST.get("sample_id")
        print("sample_id:",sampleID)

        if 'name1' not in request.POST:
            try:
                sample=Sample.objects.get(pk=int(sampleID))
                sample.delete()
            except:
                msg="删除失败！"
                return render(request, 'dataList.html',{"currentuser":user,"msg":msg})
            account=request.session["account"]
            user = User.objects.filter(account=account)[0]
            msg="删除成功！"
            return render(request, 'dataList.html',{"currentuser":user,"msg":msg})

        sample=Sample.objects.get(pk=int(sampleID))
        sample.delete()
        cache.clear()

        return dataList(request)

def deletePatient(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method == "POST":
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]

        patientID=request.POST.get("patient_id")
        print("patientID:",patientID)
        # try:
        patient=Patient.objects.get(pk=patientID)
        patient.delete()
        cache.clear()
        # except:
        #     request.session['msg']="删除失败！"
        #     return render(request, 'addData.html',{"currentuser":user,"flag":False,"name":"","msg":request.session['msg']})
        return addData(request)

def sampleDetail(request,sampleID):
    t1=time.time()
    user = checkLoginStatus(request)
    request.session['sampleID'] = sampleID
    if user=='':
        return redirect('/')
    account=request.session["account"]
    msg=request.session["msg"]
    request.session["msg"]=""
    user = User.objects.filter(account=account)[0]
    try:
        sample=Sample.objects.get(pk=sampleID)
        patient=Patient.objects.get(pk=sample.patient_id_id)
    except:
        msg="查看失败！"
        return render(request, 'dataList.html',{"currentuser":user,"msg":msg})
    score=Score.objects.filter(user_id_id=user.pk,sample_id_id=sampleID)
    ai_score=AIScore.objects.filter(sample_id_id=sampleID)

    patient.sex=patient.get_sex_display() 
    patient.ventilation_mode=patient.get_ventilation_mode_display() 
    patient.nerve_block=patient.get_nerve_block_display() 
    patient.analgesic_pump=patient.get_analgesic_pump_display() 
    sample.before_operation=sample.get_before_operation_display() 

    if sample.biology:
        sample.biology=readCsv(os.path.join(settings.MEDIA_ROOT,sample.biology.name[1:]))

    score_flag=0
    if len(score)>0:
        score_flag=1
        score=score[0]
        lianpu_list=['','A','B','C','D','E','F']
        score.sum_score=int(score.sum_score) if score.sum_score is not None else 0
        score.FLACC_score=int(score.FLACC_score) if score.FLACC_score is not None else 0
        score.cu=False if score.FACE_score is not None else True
        score.FACE_score=int(score.FACE_score) if score.FACE_score is not None else 0
        score.legs_score=int(score.legs_score) if score.legs_score is not None else 0
        score.Acitivity_score=int(score.Acitivity_score) if score.Acitivity_score is not None else 0
        score.Cry_score=int(score.Cry_score) if score.Cry_score is not None else 0
        score.consolability_score=int(score.consolability_score) if score.consolability_score is not None else 0
        score.VAS_score=int(score.VAS_score) if score.VAS_score is not None else 0
        score.lianpu_score=int(score.lianpu_score) if score.lianpu_score is not None else 1
        score.lianpu_score_zimu=lianpu_list[score.lianpu_score]
    else:
        score.sum_score=0
        score.FLACC_score=0
        score.FACE_score=0
        score.legs_score=0
        score.Acitivity_score=0
        score.Cry_score=0
        score.consolability_score=0
        score.VAS_score=0
        score.lianpu_score=1
        score.lianpu_score_zimu='A'
        score.cu=False
    score.xi=not score.cu

    print(score)

    ai=None
    ai_score_flag=1
    if len(ai_score)==0:
        ai_score_flag=0
    if ai_score_flag:
        ai=ai_score[0]
        ai.all_score=round(ai.all_score*10,2)
        ai.face_score=round(ai.face_score*10,2)
        ai.voice_score=round(ai.voice_score*10,2)
        # ai.face_score_npy_path=np.load(os.path.join(settings.MEDIA_ROOT,ai.face_score_npy_path)).tolist()
        # if ai.voice_score_npy_path:
        #     ai.voice_score_npy_path=np.load(os.path.join(settings.MEDIA_ROOT,ai.voice_score_npy_path)).tolist()
        # sum=0
        # for i in ai.voice_score_npy_path:
        #     sum+=i
        # ai.voice_score=sum/len(ai.voice_score_npy_path)
        # ai.all_score=(0.2*ai.voice_score+0.8*ai.face_score)
    t2=time.time()
    print("sample",t2-t1)
    return render(request, 'sampleDetail.html',{"currentuser":user,"msg":msg,"patient":patient,"sample":sample,"score":score,"score_flag":score_flag,"ai_score_flag":ai_score_flag,"ai_score":ai})

def readCsv(csv_path):
    ecg,gsr,hr=[],[],[]
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        lines=[line for line in reader]
        if len(lines)<2:
            return None
        for line in lines[1:]:
            line=line[0].split(';')
            ecg.append(0)
            gsr.append(float(line[0]))
            hr.append(0)

    return {"ecg":ecg,"gsr":gsr,"hr":hr}

def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def stream_video(request):
    """将视频文件以流媒体的方式响应"""
    t1=time.time()
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    path = request.GET.get('path')
  #这里根据实际情况改变，我的views.py在core文件夹下但是folder_path却只到core的上一层，media也在core文件夹下
    folder_path = os.getcwd().replace('\\', '/')
    path=folder_path+path #path就是template ？后面的参数的值
    size = os.path.getsize(path)
    print(size)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 10
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    t2=time.time()
    print("video",t2-t1)
    return resp

def addScoreSuccess(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method=="POST":
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        sampleID=request.session['sampleID']
        scores=Score.objects.filter(user_id_id=user.pk,sample_id_id=sampleID)
        values={}
        flacc_check=request.POST.get('flacc_check')
        xi_list=["FACE","legs","Acitivity","Cry","consolability"]
        for key in Score.objects.values().first().keys():
            if key[-5:]=='score':
                value=request.POST.get(key[:-5]+'input')
                if key[:-6] in xi_list:
                    value=None if flacc_check=="cu_check" or request.POST.get('FLACC_checkbox') is None else float(value)
                else:
                    value=None if request.POST.get(key[:-5]+'checkbox') is None else float(value)
                    print(key[:-5]+'checkbox',request.POST.get(key[:-5]+'checkbox'))
                values[key]=value
        print(values)
        if not scores.exists():
            values["user_id_id"]=user.pk
            values["sample_id_id"]=sampleID
            Score.objects.create(**values)
            cache.clear()
        else:
            values["add_time"]=datetime.now()
            scores.update(**values)
            cache.clear()
        #     value=request.POST.get(key)
        #     if value=="":
        #         value=None
        #     # if value is not None:
        #     #     if key=="weight":
        #     #         value=float(value)
        #     #     elif value.isdigit():
        #     #         value=int(value)
        #     values[key]=value
        # print(values)
        # Patient.objects.create(**values)
        # request.session['addData_flag'] = True
        # request.session['addData_name'] = name
        request.session['msg'] = "评分成功！"

        all_sample=Sample.objects.all()
        user = User.objects.filter(account=account)[0]
        user_score=user.score_user.all()
        tmp=[]
        for sample in all_sample:
            tmp.append(sample.pk)
        all_sample=tmp.copy()
        user_sample=[]
        # user_sample=list(all_sample.none())
        for score in user_score:
            user_sample.append(score.sample_id_id)

        for sample in all_sample:
            if sample not in user_sample:
                request.session['msg'] +=' 将进入下一个病人样本'
                return redirect("/sampleDetail/"+str(sample))

        return redirect('/dataList')

def changeName(request):
    if request.method=="POST":
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        name=request.POST.get('name')
        user.name=name
        user.save()
        request.session['msg'] = "更改昵称成功！"+name
        return redirect(request.POST.get('herf'))

def addPatientListSuccess(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method=="POST":
        file_input =request.FILES["csv"]
        save_path =os.path.join(os.path.join(settings.MEDIA_ROOT,'tmp'),file_input.name)
        with open(save_path,'wb+') as f:
            for chunk in file_input.chunks():
                f.write(chunk)

        if not save_path.endswith('.csv'):
            if save_path.endswith('.xls'):
                df = pd.read_excel(save_path) 
            elif save_path.endswith('.xlsx'):
                df = pd.read_excel(save_path,engine='openpyxl')
            else:
                request.session['msg'] = "文件格式有误！"
                return redirect('/addData')
            save_path =os.path.join(os.path.join(settings.MEDIA_ROOT,'tmp'),os.path.splitext(file_input.name)[0]+'.csv')
            df.to_csv(save_path,encoding="utf-8",index=False)
            
            
        line_num_glo=1
        patient_list=[]
        keys=Patient.objects.values().first().keys()
        try:
            with open(save_path,'r',encoding="utf-8") as f:
                reader = csv.reader(f)
                lines=[line for line in reader][1:]
                for line_num,line in enumerate(lines):
                    line_num_glo=line_num+2
                    values={}
                    line_flag=False
                    for i,key in enumerate(keys):
                        value=""
                        if key=="patient_id" or key=="add_time":
                            continue
                        else:
                            value=line[i-1]
                        if value=="" or value==".":
                            value=None
                            if key in ["name","sex","age"]:
                                line_flag=True
                                break
                        # if value is not None:
                        #     if key=="weight":
                        #         value=float(value)
                        #     elif value.isdigit():
                        #         value=int(value)
                        if value is not None:
                            if key in ["csv_id","sex","age","ventilation_mode","nerve_block","analgesic_pump"]:
                                value=int(float(value)) 
                            if key=="weight":
                                value=float(value) 
                        values[key]=value
                    if line_flag:
                        continue
                    print(values)
                    patient_obj=Patient(**values)
                    patient_list.append(patient_obj)
            Patient.objects.bulk_create(patient_list)
        except Exception as e:
            print(str(e))
            request.session['msg'] = "文件格式有误！"
            return redirect('/addData')
        request.session['msg'] = "批量添加 "+str(len(patient_list))+" 位病人成功！"
        return redirect('/addData')
        
def addDataListSuccess(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method=="POST":
        file_input =request.FILES["csv"]
        save_path =os.path.join(os.path.join(settings.MEDIA_ROOT,'tmp'),file_input.name)
        with open(save_path,'wb+') as f:
            for chunk in file_input.chunks():
                f.write(chunk)

        if not save_path.endswith('.csv'):
            if save_path.endswith('.xls'):
                df = pd.read_excel(save_path) 
            elif save_path.endswith('.xlsx'):
                df = pd.read_excel(save_path,engine='openpyxl')
            else:
                request.session['msg'] = "文件格式有误！请检查第 "+str(line_num_glo)+" 行"
                return redirect('/addData')
            save_path =os.path.join(os.path.join(settings.MEDIA_ROOT,'tmp'),os.path.splitext(file_input.name)[0]+'.csv')
            df.to_csv(save_path,encoding="utf-8",index=False)
            
            
        line_num_glo=1
        sample_list=[]
        patient_list=[]
        keys=Sample.objects.values().first().keys()
        keys=list(keys)[2:2+3]+list(keys)[2+4:2+6]
        try:
            with open(save_path,'r',encoding="utf-8") as f:
                reader = csv.reader(f)
                lines=[line for line in reader][1:]
                for line_num,line in enumerate(lines):
                    line_num_glo=line_num+2
                    if line[0]=="" or line[0]=="." or line[1]=="" or line[1]==".":
                        continue
                    patients=Patient.objects.filter(csv_id=line[0],name=line[1])
                    if len(patients)==0:
                        continue
                    patient=patients[0]
                    for i in range(4):
                        values={"patient_id_id":patient.pk,"before_operation":i+1}
                        line_flag=False
                        for j,key in enumerate(keys):
                            value=""
                            # if key in ["sample_id","patient_id_id","add_time"]:
                            #     continue
                                
                            value=line[i*5+2+j]
                            
                            if value=="" or value==".":
                                value=None
                                if key in ["video"]:
                                    line_flag=True
                                    break
                            if value is not None:
                                if key not in ["video","biology"]:
                                    value=int(float(value)) 
                                else:
                                    prestr="/mp4/" if key=="video" else "/csv/"
                                    value=prestr+value
                            values[key]=value
                        if line_flag:
                            continue
                        print(values)
                        sample_obj=Sample(**values)
                        sample_list.append(sample_obj)
                        patient_list.append(patients)
            # Sample.objects.bulk_create(sample_list)
        except Exception as e:
            print(str(e))
            request.session['msg'] = "文件格式有误！请检查第 "+str(line_num_glo)+" 行"
            return redirect('/addData')
        request.session['msg'] = "批量添加 "+str(len(sample_list))+" 个样本成功！"
        return redirect('/addData')

#mia
def mia(request):
    return render(request, 'mia.html')
#lyon

#___________________________________________________________________________________________________________________________________
# def my_api_view(request):
#     if request.method == 'POST':
#         video = request.FILES['video']
#         # save the video file and analyze it asynchro/etc/nginx/sites-enabled/pain.confnously using your AI model
#         analyze_video.delay(video)
#         data = {'status': 'success'}
#         return JsonResponse(data)
#     else:
#         data = {'status': 'error'}
#         return JsonResponse(data)

def catch_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("服务器内部错误！!!!")
            print(e.args)
            data={"status":android_get_status(False,200),"msg":"服务器内部错误！"}
            return JsonResponse(data)
    return wrapper

def test(request):
    if request.method == 'POST':
        msg=request.POST.get('msg')
        msg='my echo: '+msg+' ,done it!'
        data={'receive':msg}
        return JsonResponse(data)
    else:
        priviousAIscore()
        data={'receive':'get'}
        return JsonResponse(data)

def android_get_status(flag,code=100):
    if flag==True:
        code=100
    return {"flag":flag,"code":code}

def android_tokentest(request):
    flg=False
    user=None
    data=None
    if request.META.get("HTTP_TOKEN") is None:
        data={"status":android_get_status(False,402),"msg":"token错误！"}
        return user,data,flg
    UserToken.cleanup_expired_tokens()  # 清理过期的token
    res1=UserToken.objects.filter(key=request.META.get("HTTP_TOKEN"))
    if res1:
        res = res1[0]
        user=res.user
        flg=True
    else:
        data={"status":android_get_status(False,402),"msg":"token错误！"}
    return user,data,flg

@catch_exceptions
def android_postlogin(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    if request.method == "POST":

        request_data =json.loads(request.body)
        userName = request_data.get('account')
        userPassword=request_data.get('password')
        res1 = User.objects.filter(account=userName)
        data={"status":android_get_status(False,400),"msg":"账号不存在！"}
        if res1:
            res = res1[0]
            if check_password(userPassword, res.password):
                UserToken.cleanup_expired_tokens()  # 清理过期的token
                token, _ = UserToken.objects.get_or_create(user=res)
                data={"status":android_get_status(True),"msg":"登录成功！","user":{"account":res.account,"name":res.name},"token":token.key}
            else:
                data={"status":android_get_status(False,401),"msg":"用户名或密码错误！"}
    return JsonResponse(data)

@catch_exceptions
def android_postpatient(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    user,data,flg=android_tokentest(request)
    if flg and request.method == "POST":
        request_data =json.loads(request.body)
        keys=["name","sex","age","note"]
        values={}
        # for key in Patient.objects.values().first().keys():
        #     value=""
        #     if key=="patient_id" or key=="add_time":
        #         continue
        #     else:
        #         value=request_data.get(key)
        #     if value=="":
        #         value=None
        #     if value is not None:
        #         if key in ["csv_id","sex","age","ventilation_mode","nerve_block","analgesic_pump"]:
        #             value=int(float(value)) 
        #         if key=="weight":
        #             value=float(value) 
        #     values[key]=value
        for key in keys:
            value=request_data.get(key)
            if value is not None:
                if key in ["sex","age"]:
                    value=int(float(value))
                    # if key=="age":
                    #     value=0 if value==0 else 1 if value==1 else 3 if value==2 else 7
                values[key]=value
        if 'note' in values.keys():
            values["diagnose"]=values.pop('note')
        print(values)
        try:
            patient=Patient.objects.create(**values)
        except IntegrityError as e:
            print(e.args)
            data={"status":android_get_status(False,406),"msg":"添加病人失败！原因："+str(e.args)}
        else:
            cache.clear()
            data={"status":android_get_status(True),"msg":"添加病人成功！","patientID":patient.pk}
    return JsonResponse(data)

@catch_exceptions
def android_postvideo(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    user,data,flg=android_tokentest(request)
    if flg and request.method == "POST":
        data={"status":android_get_status(False,404),"msg":"视频上传失败！"}
        video = request.FILES['video']
        patient_id = request.META.get('HTTP_PATIENTID')
        res=Patient.objects.filter(pk=patient_id)
        if video and patient_id and len(res)>0:
            print("upload name:",video.name)
            file_name = 'mp4/Android/' + str(patient_id)+'-'+str(res[0].patient_sample.count()+1)+'_Android.mp4'
            file_name = default_storage.save(file_name, video)

            bio_flg=False
            bio_msg=""
            data_list =request.POST.get('biology')
            if not data_list:
                bio_msg="没有生理信号！"
            else: 
                data_list=json.loads(data_list)
                print(data_list)
                maxnlen=max(len(value) for value in data_list.values())
                if maxnlen<1:
                    bio_msg="没有生理信号！"
                else:
                    csv_name='csv/'+str(file_name)[4:-4]+'.csv'
                    try:
                        with open(os.path.join(settings.MEDIA_ROOT,csv_name), 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(data_list.keys())
                            for i in range(100000):
                                key_flg=False
                                row=[]
                                for k in data_list.keys():
                                    if i<len(data_list[k]):
                                        key_flg=True
                                        row.append(data_list[k][i])
                                    else:
                                        row.append("")
                                if not key_flg:
                                    break
                                writer.writerow(row)
                        
                    except Exception as e:
                        bio_msg="生理信号失败！原因："+str(e.args)
                    else:
                        bio_flg=True
                        bio_msg="生理信号上传成功！"


            if file_name:
                values={}
                values["video"]='/'+file_name
                values["patient_id_id"]=patient_id
                if bio_flg:
                    values['biology']= '/'+csv_name
                print(values)
                try:
                    sample=Sample.objects.create(**values)
                except:
                    data={"status":android_get_status(False,407),"msg":"添加视频样本失败！"+bio_msg}
                else:
                    cache.clear()
                    sampleID=sample.pk
                    values["sample_id"]=sampleID
                    t=myThread(sampleID,os.path.join(settings.MEDIA_ROOT,file_name))
                    t.start()
                    
                    data={"status":android_get_status(True),"msg":"视频上传成功！"+bio_msg,"sampleID":sampleID}
    return JsonResponse(data)

@catch_exceptions
def android_postscore(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    user,data,flg=android_tokentest(request)
    if flg and request.method == "POST":
        request_data =json.loads(request.body)
        sampleID=request_data.get('sampleID')
        scores=Score.objects.filter(user_id_id=user.pk,sample_id_id=sampleID)
        values={}
        keys=["sum_score","FACE_score","legs_score","Acitivity_score","Cry_score","consolability_score","heart_rate","diastolic_pressure","systolic_pressure"]
        flacc_score=0
        flag=False
        for key in keys:
            value=request_data.get(key)
            value=None if value is None else float(value)
            values[key]=value
            if key not in ["sum_score","heart_rate","diastolic_pressure","systolic_pressure"] and value is not None:
                flacc_score+=value
                flag=True
        # for key in Score.objects.values().first().keys():
        #     if key[-5:]=='score':
        #         value=request_data.get(key)
        #         value=None if value is None else float(value)
        #         values[key]=value
        #         if key in xi_list and value is not None:
        #             flacc_score+=value
        #             flag=True

        print(values)
        if not flag:
            data={"status":android_get_status(False,403),"msg":"评分失败！"}
        else:
            values["FLACC_score"]=flacc_score
            if not scores.exists():
                values["user_id_id"]=user.pk
                values["sample_id_id"]=sampleID
                try:
                    score=Score.objects.create(**values)
                except:
                    data={"status":android_get_status(False,403),"msg":"评分失败！"}
                else:
                    cache.clear()
                    data={"status":android_get_status(True),"msg":"评分成功！","scoreID":score.pk,"FLACC_score":flacc_score}
            else:
                values["add_time"]=datetime.now()
                try:
                    scores.update(**values)
                except:
                    data={"status":android_get_status(False,403),"msg":"评分失败！"}
                else:
                    cache.clear()
                    score=scores[0]
                    data={"status":android_get_status(True),"msg":"评分成功！","scoreID":score.pk,"FLACC_score":flacc_score}
        if data["status"]["flag"]==True:
            try:
                sample=Sample.objects.get(pk=sampleID)
                sample.heart_rate=values["heart_rate"]
                sample.diastolic_pressure=values["diastolic_pressure"]
                sample.systolic_pressure=values["systolic_pressure"]
                sample.save()
            except:
                data={"status":android_get_status(False,411),"msg":"心率血压上传失败！"}
    return JsonResponse(data)

@catch_exceptions
def android_getAIscore(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    user,data,flg=android_tokentest(request)
    if flg and request.method == "GET":
        sampleID = request.META.get('HTTP_SAMPLEID')
        ai_scores=AIScore.objects.filter(sample_id_id=sampleID)
        if len(ai_scores)>0:
            ai_score=ai_scores[0]
            ret={}
            ret["all_score"]=format(ai_score.all_score*10,'.1f') if ai_score.all_score is not None else '空'
            ret["face_score"]=format(ai_score.face_score*10,'.1f') if ai_score.face_score is not None else '空'
            ret["voice_score"]=format(ai_score.voice_score*10,'.1f') if ai_score.voice_score is not None else '空'
            ret["heart_rate"]=int(ai_score.heart_rate) if ai_score.heart_rate is not None else '空'
            ret["diastolic_pressure"]=int(ai_score.systolic_pressure) if ai_score.systolic_pressure is not None else '空'
            ret["systolic_pressure"]=int(ai_score.diastolic_pressure) if ai_score.diastolic_pressure is not None else '空'
            print(ret,ai_score.systolic_pressure,ai_score.diastolic_pressure)
            # if ret["all_score"]<0:
            #     ret["all_score"]="该视频缺少人脸或声音！"
            # if ret["face_score"]<0:
            #     ret["face_score"]="该视频未检测到人脸！"
            # if ret["voice_score"]<0:
            #     ret["voice_score"]="该视频未含声音！"
            data={"status":android_get_status(True),"msg":"AI评分完成！","AIscore":ret}
        else:
            data={"status":android_get_status(False,405),"msg":"AI正在评分中,请稍等半分钟！"}
    return JsonResponse(data)

def priviousAIscore():
    res=Sample.objects.filter(pk__lt=1110)
    for sample in res:
        t=myThread(sample.pk,os.path.join(settings.MEDIA_ROOT,str(sample.video)[1:]))
        t.start()
    return True

@catch_exceptions
def android_receiveCSV(request):
    data={"status":android_get_status(False,500),"msg":"请求方式错误！"}
    user,data,flg=android_tokentest(request)
    if flg and request.method == "POST":
        request_data =json.loads(request.body)
        sampleID=request_data.get('sampleID')
        if not sampleID:
            data={"status":android_get_status(False,408),"msg":"未找到样本ID！"}
        samples=Sample.objects.filter(sample_id=sampleID)
        if len(samples)==0:
            data={"status":android_get_status(False,408),"msg":"未找到样本ID！"}
        sample=samples[0]
        data_list=request_data.get('data_list')
        if not data_list or len(data_list)==0:
            data={"status":android_get_status(False,409),"msg":"没有序列！"}
        csv_name='csv'+str(sample.video)[4:-4]+'.csv'
        print(csv_name)
        try:
            with open(os.path.join(settings.MEDIA_ROOT,csv_name), 'w', newline='') as f:
                writer = csv.writer(f)
                for i in data_list:
                    writer.writerow([i])
            sample.biology = '/'+csv_name
            sample.save(update_fields=['biology'])
        except Exception as e:
            data={"status":android_get_status(False,410),"msg":"评分失败！原因："+str(e.args)}
        else:
            cache.clear()
            data={"status":android_get_status(True),"msg":"样本上传成功！","sampleID":sampleID}
    return JsonResponse(data)

# def add_previous():
    with open('/hdd/sdb1/lzq/pain/add_previous.csv', 'r') as f:
        from django.db.models import Q
        reader = csv.reader(f)
        lines=[line for line in reader]
        score_list=[]
        for line in lines[2:]:
            try:
                csv_id=int(line[0])
            except:
                continue
            scores=[[line[2],*line[4:10]],[line[3],*line[10:16]],[line[36],*line[38:44]],[line[37],*line[44:50]]]
            patient = Patient.objects.filter(csv_id=csv_id)
            if len(patient)==0:
                continue 
            else:
                patient=patient[0]
            for i in range(2):
                sample = Sample.objects.filter(Q(patient_id=patient.patient_id) & Q(before_operation=(i+1)*2))
                if len(sample)==0:
                    continue 
                else:
                    sample=sample[0]
                for j,score in enumerate(scores[i*2:(i+1)*2]):
                    values={}
                    key_list=["sum_score","FLACC_score","FACE_score","legs_score","Acitivity_score","Cry_score","consolability_score"]
                    for k,key in enumerate(key_list):
                        try:
                            values[key]=float(score[k]) if key!='sum_score' else float(score[k])/10
                        except:
                            values[key]=None
                    if values['FLACC_score'] is None:
                        continue
                    values["user_id_id"]=j+17
                    values["sample_id_id"]=sample.pk
                    print(values)
                    score_obj=Score(**values)
                    score_list.append(score_obj)
        Score.objects.bulk_create(score_list)
