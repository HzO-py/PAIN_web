"""PAIN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^index/', views.index, name='index'),
    url(r'^sampleDetail/(\d+)/$', views.sampleDetail, name='sampleDetail'),
    url(r'^stream_video/$', views.stream_video, name='stream_video'),
    url(r'^postlogin/$', views.postlogin, name='postlogin'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^postregister/$', views.postregister, name='postregister'),
    url(r'^addData/$', views.addData, name='addData'),
    url(r'^addPatientSuccess/', views.addPatientSuccess, name='addPatientSuccess'),
    url(r'^addPatientListSuccess/', views.addPatientListSuccess, name='addPatientListSuccess'),
    url(r'^addPatientDataSuccess/', views.addPatientDataSuccess, name='addPatientDataSuccess'),
    url(r'^addDataListSuccess/', views.addDataListSuccess, name='addDataListSuccess'),
    url(r'^dataList/', views.dataList, name='dataList'),
    url(r'^scoreList/', views.scoreList, name='scoreList'),
    url(r'^addScoreSuccess/', views.addScoreSuccess, name='addScoreSuccess'),
    url(r'^changeName/', views.changeName, name='changeName'),
    url(r'^export_excel/', views.export_excel, name='export_excel'),
    # url(r'^mia/', views.mia, name='mia'),
    url(r'^deleteSample/', views.deleteSample, name='deleteSample'),
    url(r'^deletePatient/', views.deletePatient, name='deletePatient'),
    url(r'^my-api/test', views.test, name='test'),

    url(r'^android/android_postlogin', views.android_postlogin, name='android_postlogin'),
    url(r'^android/android_postpatient', views.android_postpatient, name='android_postpatient'),
    url(r'^android/android_postvideo', views.android_postvideo, name='android_postvideo'),
    url(r'^android/android_postscore', views.android_postscore, name='android_postscore'),
    url(r'^android/android_getAIscore', views.android_getAIscore, name='android_getAIscore'),
    url(r'^android/android_receiveCSV', views.android_receiveCSV, name='android_receiveCSV'),

    # url(r'^android/android_priviousAIscore', views.android_priviousAIscore, name='android_priviousAIscore')
]
