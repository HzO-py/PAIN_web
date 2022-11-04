from django.shortcuts import render,redirect
from patient.models import *
from django.core import serializers
import json
import datetime
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.db.models import F
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

class myThread(threading.Thread):
    def __init__(self, sampleID,videopath):
        threading.Thread.__init__(self)
        self.sampleID=sampleID
        self.videopath=videopath

    def run(self):
        print("thread start!!")
        face_score,face_mp4_path,face_score_npy_path,voice_score,voice_score_npy_path=ai_main(self.videopath)
        AIScore.objects.create(sample_id_id=self.sampleID,face_score=face_score,face_mp4_path=face_mp4_path,face_score_npy_path=face_score_npy_path,voice_score=voice_score,voice_score_npy_path=voice_score_npy_path)
        print("thread done!!")


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
            row['sample_num']=patient.sample_num
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
            if key=="sample_num":
                value=0
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
        print(request.POST)
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
                Patient.objects.filter(pk=value).update(sample_num=F('sample_num') + 1)
            values[key]=value
        
        print(values)
        sample=Sample.objects.create(**values)
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
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["patient_id"]=patient.pk
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
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["patient_id"]=patient.pk
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            row["sum"]=score.sum_score
            row["FLACC"]=score.FLACC_score
            row["VAS"]=score.VAS_score
            row["lianpu"]=lianpu_list[int(score.lianpu_score)] if score.lianpu_score is not None else None
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

def scoreList(request):
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

        all_sample=Sample.objects.all()
        all_score=Score.objects.all()
        print("all_score")
        print(all_score)
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
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["patient_id"]=patient.pk
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
            scores=Score.objects.filter(sample_id_id=rest.pk)
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["patient_id"]=patient.pk
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["video_name"]=rest.video.name.split('/')[-1]
            row["biology_name"]=rest.biology.name.split('/')[-1] if rest.biology else '空'
            sum_tmp=scores.aggregate(Avg("sum_score"))["sum_score__avg"]
            row["sum"]=round(sum_tmp,2) if sum_tmp is not None else None
            FLACC_tmp=scores.aggregate(Avg("FLACC_score"))["FLACC_score__avg"] 
            row["FLACC"]=round(FLACC_tmp,2) if FLACC_tmp is not None else None
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
        return render(request, 'scoreList.html',{"currentuser":user,"msg":msg})

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
    sample=Sample.objects.get(pk=sampleID)
    patient=Patient.objects.get(pk=sample.patient_id_id)
    score=Score.objects.filter(user_id_id=user.pk,sample_id_id=sampleID)
    # ai_score=AIScore.objects.filter(sample_id_id=sampleID)

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
    ai_score_flag=0
    # if len(ai_score)==0:
    #     ai_score_flag=0
    # if ai_score_flag:
    #     ai=ai_score[0]
    #     ai.face_score_npy_path=np.load(os.path.join(settings.MEDIA_ROOT,ai.face_score_npy_path)).tolist()
    #     if ai.voice_score_npy_path:
    #         ai.voice_score_npy_path=np.load(os.path.join(settings.MEDIA_ROOT,ai.voice_score_npy_path)).tolist()
    #     sum=0
    #     for i in ai.voice_score_npy_path:
    #         sum+=i
    #     ai.voice_score=sum/len(ai.voice_score_npy_path)
    #     ai.all_score=(0.2*ai.voice_score+0.8*ai.face_score)
    t2=time.time()
    print("sample",t2-t1)
    return render(request, 'sampleDetail.html',{"currentuser":user,"msg":msg,"patient":patient,"sample":sample,"score":score,"score_flag":score_flag,"ai_score_flag":ai_score_flag,"ai_score":ai})

def readCsv(csv_path):
    ecg,gsr,hr=[],[],[]
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        lines=[line for line in reader]
        for line in lines:
            line=line[0].split(';')
            ecg.append(float(line[1]))
            gsr.append(float(line[3]))
            hr.append(float(line[4]))

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
        else:
            values["add_time"]=datetime.now()
            scores.update(**values)
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
                        if key=="sample_num":
                            value=0
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
            for patient in patient_list:
                patient.update(sample_num=F('sample_num') + 1)
        except Exception as e:
            print(str(e))
            request.session['msg'] = "文件格式有误！请检查第 "+str(line_num_glo)+" 行"
            return redirect('/addData')
        request.session['msg'] = "批量添加 "+str(len(sample_list))+" 个样本成功！"
        return redirect('/addData')