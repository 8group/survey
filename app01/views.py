from django.db.models import Count
from django.shortcuts import render,HttpResponse,redirect
from app01 import models

# Create your views here.

def deal_page(request,page):
    print(page)
    return render(request, 'muban/'+page+'.html')

def survey_list(request):
    survey_list = models.SurveyInfo.objects.all().annotate(stu_count=Count("cls__userinfo"))\
        .values('id','title','cls_id','creator_id','stu_count','cls__name')
    # print('============',survey_list)

    for x in survey_list:
        print('---------',x)
    return render(request, 'muban/survey_list.html',locals())
