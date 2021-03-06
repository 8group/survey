from django.db.models import Count
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from app01 import models

from app01.forms import QuestionForm,OptionModelForm,SurveyModelForm
import json



# Create your views here.


def add_survey(request):
    """
    新增问卷页面
    :param request:
    :return:
    """
    if request.method == 'GET':
        survey_form = SurveyModelForm()
        return render(request, 'muban/add_survey.html', {'survey_form':survey_form})
    else:
        # print(request.POST)
        # title, cls_id = request.POST.get('title'), request.POST.get('cls')
        survey_form = SurveyModelForm(request.POST)
        if survey_form.is_valid():
            survey_form.save()
            return redirect('/survey_list/')
        else:
            return render(request, 'muban/add_survey.html', {'survey_form':survey_form})

def deal_page(request,page):
    """
    处理模板中暂时不需要的页面
    :param request: 
    :param page: 
    :return: 
    """
    print(page)
    return render(request, 'muban/'+page+'.html')

def survey_list(request):
    """
    问卷列表页面
    :param request:
    :return:
    """
    survey_list = models.SurveyInfo.objects.all().annotate(stu_count=Count("cls__userinfo"))\
        .values('id', 'title', 'cls_id', 'creator_id', 'stu_count', 'cls__name')

    return render(request, 'muban/survey_list.html',locals())

class Opt_g(object):
    """
    接收选项列表
    将每个选项元素中添加一个Form组件
    返回问题列表生成器
    """
    def __init__(self,data):
        self.data = data

    def __iter__(self):
        for x in self.data:
            x.form = OptionModelForm(instance=x)
            yield x

class Que_g(object):
    """
    接收问题列表
    将每个问题元素中添加一个Form组件
    返回问题列表生成器
    """
    def __init__(self,data):
        self.data = data

    def __iter__(self):
        if not self.data:  # 没有问题的问卷
            yield {'option_class': 'hide', 'options': [], 'form': QuestionForm()}
        else: # 有问题的问卷
            for x in self.data:
                x.form = QuestionForm(initial={'value': x.name, 'type': x.type})
                x.options = []
                x.option_class = 'hide'
                if x.type == 2:
                    x.option_class = ''
                    options = models.Option.objects.filter(question_id=x.id)
                    x.options = Opt_g(options)
                yield x


def edit_survey(request):
    """
    编辑问卷页面，返回所选问卷包含的问题列表等信息
    :param request:
    :return:
    """
    survey_id = request.GET.get('survey_id')
    question_list = models.Question.objects.filter(surveyinfo_id=survey_id)
    question_list = Que_g(question_list)
    # for x in question_list:
    #     for y in x.options:
    #         print(y)

    name_dict={
        'survey_id':survey_id,
        'question_list':question_list,
        'questionForm':QuestionForm(),
        'optionModelForm':OptionModelForm()
    }
    return render(request, 'muban/edit_survey.html',name_dict)




def deal_edit(request):
    """
    接受ajax请求，修改问卷中包含的问题
    :param request:
    :return:
    """
    response = {'success':True}
    survey_id = request.GET.get("survey_id")
    data = json.loads(request.POST.get('data'))
    new_que_list = []
    old_que_list = models.Question.objects.filter(surveyinfo_id=survey_id).values_list('id')
    old_que_list = [str(x[0]) for x in old_que_list]

    print("===========", data)
    with transaction.atomic():
        for question in data:
            que_id, que_name, que_type, options = question.get("question_id"),question.get("question_name"),question.get("question_type"),question.get("options")
            if que_id:  # 修改问题
                new_que_list.append(que_id)  # 记录问题ID
                models.Question.objects.filter(pk=que_id).update(name=que_name,type=que_type)
                if que_type == '2' and options:
                    for option in options:
                        opt_id, opt_name, opt_score = option.get('option_id'), option.get('option_value'), option.get('option_key')
                        if opt_id:  # 修改选项
                            models.Option.objects.filter(pk=opt_id).update(name=opt_name, score=opt_score)
                        else:  # 新增选项
                            models.Option.objects.create(name=opt_name, score=opt_score, question_id=que_id)
            else:  # 新增问题
                que_obj = models.Question.objects.create(name=que_name, type=que_type, surveyinfo_id=survey_id)
                new_que_list.append(que_obj.id)  # 记录问题ID
                if que_type == '2' and options:  # 新增选项
                    for option in options:
                        opt_name, opt_score = option.get('option_value'), option.get('option_key')
                        models.Option.objects.create(name=opt_name, score=opt_score, question_id=que_obj.id)

        # 旧的问题列表与新的作比对
        print(old_que_list,new_que_list)
        for que_id in old_que_list:
            if que_id not in new_que_list:  # 如果旧的问题已经不存在
                models.Question.objects.filter(pk=que_id).delete()  # 删除问题
                models.Option.objects.filter(question_id=que_id).delete()  # 删除选项

    return JsonResponse(response)