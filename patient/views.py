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
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

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
        name = request.POST['name']
        phoneNum = request.POST['phoneNum']
        # verifyCode = request.POST['verifyCode']
        
        # m = hashlib.md5()
        # m.update(password.encode('utf-8'))
        password = make_password(password, 'sha', 'pbkdf2_sha256')
        
        User.objects.create(account=phoneNum,password=password,name=name)
        # res = User.objects.get(username=phoneNum)
        

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
        res=Patient.objects.all()
        patient_list=[]
        for patient in res:
            row={}
            row['pk']=patient.pk
            row['name']=patient.name
            row['sex']=patient.get_sex_display()
            row['age']=patient.age
            row['add_time']=patient.add_time.strftime('%Y-%m-%d %H:%M:%S')
            row['sample_num']=patient.sample_num
            patient_list.append(row)
        json_data=json.dumps(patient_list, ensure_ascii=False)
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
            # if value is not None:
            #     if key=="weight":
            #         value=float(value)
            #     elif value.isdigit():
            #         value=int(value)
            values[key]=value
        print(values)
        Patient.objects.create(**values)
        request.session['addData_flag'] = True
        request.session['addData_name'] = name
        request.session['msg'] = "添加病人 "+name+" 成功！"
        return redirect('/addData')
        #return HttpResponse(str,content_type='text/plain;charset=utf-8')
            
        
    #return render(request, 'addData.html')

def searchPatient(request):
    user = checkLoginStatus(request)
    if user=='':
        return redirect('/')
    if request.method=="POST":
        name=request.POST.get("name")
        print(name)
        res=Patient.objects.filter(name__contains=name)
        json_data = serializers.serialize('json', res)
        print(json_data)
        return HttpResponse(json_data,content_type='application/json')

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
        lang=request.POST.get('lang')
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
                request.session['lang'] = lang
                request.session["msg"]=""
                checkIsLogin(request)
                print(request.session['account'])
                return redirect('/dataList')
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
        all_sample=Sample.objects.all()
        user = User.objects.filter(account=account)[0]
        user_score=user.score_user.all()
        tmp=[]
        for sample in all_sample:
            tmp.append(sample.pk)
        all_sample=tmp
        user_sample=[]
        # user_sample=list(all_sample.none())
        for score in user_score:
            user_sample.append(score.sample_id_id)

        rest_sample=[]
        for sample in all_sample:
            if sample not in user_sample:
                rest_sample.append(sample)
        
        user_sample=Sample.objects.filter(pk__in=user_sample)
        rest_sample=Sample.objects.filter(pk__in=rest_sample)
        
        
        
        rest_list=[]
        for rest in rest_sample:
            row={}
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["sex"]=patient.get_sex_display()
            row["age"]=patient.age
            row["video_name"]=rest.video.name.split('/')[-1]
            row["add_time"]=rest.add_time.strftime('%Y-%m-%d %H:%M:%S')
            rest_list.append(row)

        user_list=[]
        for rest in user_sample:
            row={}
            score=Score.objects.get(sample_id_id=rest.pk,user_id_id=user.pk)
            patient=Patient.objects.get(pk=rest.patient_id_id)
            row["sample_id"]=rest.pk
            row["name"]=patient.name
            row["video_name"]=rest.video.name.split('/')[-1]
            row["sum"]=score.sum_score
            row["FLACC"]=score.FLACC_score
            row["VAS"]=score.VAS_score
            row["lianpu"]=score.lianpu_score
            row["add_time"]=score.add_time.strftime('%Y-%m-%d %H:%M:%S')
            user_list.append(row)
            
        output={"rest_list":rest_list,"done_list":user_list}
        for k,v in output.items():
            for i in range(len(v)):
                for kk,vv in v[i].items():
                    if vv==None:
                        output[k][i][kk]='空'

        json_data=json.dumps(output, ensure_ascii=False)

        return HttpResponse(json_data,content_type='application/json')
        
    else:
        account=request.session["account"]
        user = User.objects.filter(account=account)[0]
        msg=request.session['msg']
        request.session['msg']=""
        return render(request, 'dataList.html',{"currentuser":user,"msg":msg})

def sampleDetail(request,sampleID):
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
        sample.biology=readCsv(os.path.join(settings.MEDIA_ROOT,sample.biology.name))

    score_flag=0
    if len(score)>0:
        score_flag=1
        score=score[0]
        lianpu_list=['','A','B','C','D','E','F']
        score.sum_score=int(score.sum_score) if score.sum_score else 0
        score.FLACC_score=int(score.FLACC_score) if score.FLACC_score else 0
        score.cu=False if score.FACE_score else True
        score.FACE_score=int(score.FACE_score) if score.FACE_score else 0
        score.legs_score=int(score.legs_score) if score.legs_score else 0
        score.Acitivity_score=int(score.Acitivity_score) if score.Acitivity_score else 0
        score.Cry_score=int(score.Cry_score) if score.Cry_score else 0
        score.consolability_score=int(score.consolability_score) if score.consolability_score else 0
        score.VAS_score=int(score.VAS_score) if score.VAS_score else 0
        score.lianpu_score=int(score.lianpu_score) if score.lianpu_score else 1
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
        score.cu=True
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

    return render(request, 'sampleDetail.html',{"currentuser":user,"msg":msg,"patient":patient,"sample":sample,"score":score,"score_flag":score_flag,"ai_score_flag":ai_score_flag,"ai_score":ai})

def readCsv(csv_path):
    ecg,gsr=[],[]
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        lines=[line for line in reader]
        for line in lines:
            line=line[0].split(';')
            ecg.append(float(line[1]))
            gsr.append(float(line[3]))

    return {"ecg":ecg,"gsr":gsr}

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
    print(resp)
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
                value=None if key[:-6] in xi_list and flacc_check=="cu_check" else float(value)
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