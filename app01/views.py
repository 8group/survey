from django.db.models import Count
from django.db.transaction import atomic
from django.http.response import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from app01 import models

from app01.forms import QuestionForm
import json



# Create your views here.

def deal_page(request,page):
    print(page)
    return render(request, 'muban/'+page+'.html')

def survey_list(request):
    survey_list = models.SurveyInfo.objects.all().annotate(stu_count=Count("cls__userinfo"))\
        .values('id','title','cls_id','creator_id','stu_count','cls__name')
    # print('============',survey_list)

    # for x in survey_list:
    #     print('---------',x)
    return render(request, 'muban/survey_list.html',locals())

class Que_g:
    def __init__(self,data):
        self.data = data

    def __iter__(self):
        for x in self.data:
            x['form'] = QuestionForm(initial={'value': x['name'], 'type': x['type']})
            yield x


def edit_survey(request):
    survey_id = request.GET.get('survey_id',1)
    question_list = models.Question.objects.filter(surveyinfo_id=survey_id).values('name','type')
    question_list = Que_g(question_list)


    name_dict={
        'survey_id':survey_id,
        'question_list':question_list,
        'questionForm':QuestionForm(initial={'value': "", 'type': ""})
    }
    return render(request, 'muban/edit_survey.html',name_dict)




def deal_edit(request):
    response = {'success':True}
    survey_id = request.GET.get("survey_id")
    data = json.loads(request.POST.get('data'))



    # survey_obj = models.SurveyInfo.objects.filter(pk=survey_id).first()
    # print("---------",survey_obj.question_set)
    # for x in survey_obj.question_set.all():
    #     print(x)

    with atomic():
        # 删除原有问题
        models.Question.objects.filter(surveyinfo_id=survey_id).delete()
        # 添加新问题
        for x in data:
            models.Question.objects.create(name=x['question_name'],type=x['question_type'],surveyinfo_id=survey_id)



    return JsonResponse(response)