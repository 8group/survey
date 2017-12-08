import json
import time
import datetime

from collections import defaultdict

from django.core.validators import RegexValidator
from django.db.models import Count
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import render,HttpResponse,redirect

from app01 import models

from app01.forms import QuestionForm,OptionModelForm,SurveyModelForm




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
    response = {'success':True,'msg':[]}
    survey_id = request.GET.get("survey_id")
    data = json.loads(request.POST.get('data'))
    new_que_list = []
    old_que_list = models.Question.objects.filter(surveyinfo_id=survey_id).values_list('id')
    old_que_list = [str(x[0]) for x in old_que_list]

    print("===========", data)

    with transaction.atomic():
        for question in data:
            que_id, que_name, que_type, options = question.get("question_id"), question.get("question_name"), question.get(
                "question_type"), question.get("options")
            questionForm = QuestionForm(data={'name':que_name,'type':que_type})
            if questionForm.is_valid():
                if que_id:  # 修改问题
                    new_que_list.append(que_id)  # 记录问题ID
                    models.Question.objects.filter(pk=que_id).update(name=que_name, type=que_type)
                    if que_type == '2' and options:
                        for option in options:
                            opt_id, opt_name, opt_score = option.get('option_id'), option.get(
                                'option_value'), option.get('option_key')
                            if opt_id:  # 修改选项
                                models.Option.objects.filter(pk=opt_id).update(name=opt_name, score=opt_score)
                            else:  # 新增选项
                                models.Option.objects.create(name=opt_name, score=opt_score, question_id=que_id)
                    else:
                        models.Option.objects.filter(question_id=que_id).delete()
                else:  # 新增问题
                    que_obj = models.Question.objects.create(name=que_name, type=que_type, surveyinfo_id=survey_id)
                    new_que_list.append(que_obj.id)  # 记录问题ID
                    if que_type == '2' and options:  # 新增选项x`
                        for option in options:
                            opt_name, opt_score = option.get('option_value'), option.get('option_key')
                            models.Option.objects.create(name=opt_name, score=opt_score, question_id=que_obj.id)
            else:
                response['success'] = False
                response['msg'].append({que_id:questionForm.errors})

                RegexValidator


        if response['success']:
            # 旧的问题列表与新的作比对
            print(old_que_list, new_que_list)
            del_list = set(old_que_list).difference(new_que_list)
            print(del_list)
            models.Question.objects.filter(pk__in=del_list).delete()  # 删除选项
            # for que_id in old_que_list:
            #     if que_id not in new_que_list:  # 如果旧的问题已经不存在
            #         models.Question.objects.filter(pk=que_id).delete()  # 删除问题
            #         models.Option.objects.filter(question_id=que_id).delete()  # 删除选项

    return JsonResponse(response)


def pretend_login(request,username,password):
    """
    伪造登陆信息
    :param request:
    :param username:
    :param password:
    :return:
    """
    user = models.UserInfo.objects.filter(username=username, password=password).first()
    if user:
        request.session['userinfo'] = {'id':user.id,'username':user.username}
    return

def answer(request,cls_id,survey_id):
    print(cls_id,survey_id)
    pretend_login(request,"maxiaotiao","123456a")
    user_id = request.session['userinfo']['id']
    # 当前登录用户是否是要评论的班级的学生
    ct1 = models.UserInfo.objects.filter(id=user_id,cls_id=cls_id).count()
    if not ct1:
        return HttpResponse('不是本班学生')
    # 你是否已经提交过当前问卷答案
    ct2 = models.Answer.objects.filter(student_id=user_id,question__surveyinfo_id=survey_id).count()
    print(ct2)
    if ct2:
        return HttpResponse('不能重复提交')

    from django.forms import Form
    from django.forms import fields
    from django.forms import widgets
    from django.core.exceptions import ValidationError

    def len_check(val):
        # 评价不能小于5个字
        if len(val) < 5:
            raise ValidationError('不能小于5个字')

    question_list = models.Question.objects.filter(surveyinfo_id=survey_id).all()
    field_dict = {}
    for question in question_list:
        # 根据不同的问题类型，动态生成Form中的字段
        if question.type == 1:
            field_dict["val_%s"%question.id] = fields.ChoiceField(
                label=question.name,
                error_messages={
                    'required': '分值不能为空'
                },
                widget=widgets.RadioSelect(),
                choices=[(i,i) for i in range(1,11)]
            )
        elif question.type == 2:
            field_dict["option_id_%s" % question.id] = fields.ChoiceField(
                label=question.name,
                error_messages={
                    'required': '选项不能为空'
                },
                widget=widgets.Select(attrs={'class':'dfinput-sm'}),
                choices=models.Option.objects.filter(question_id=question.id).values_list('id','name')
            )
        else:
            field_dict["content_%s" % question.id] = fields.CharField(
                label=question.name,
                error_messages={
                    'required': '选项不能为空'
                },
                widget=widgets.Textarea(attrs={'class':'dfinput'}),
                validators=[len_check,]
            )

    # 类的第二种创建方式
    AnswerForm = type("AnswerForm", (Form,), field_dict)

    if request.method == 'GET':
        answerForm = AnswerForm()
        return render(request,"muban/answer.html",{'answerForm':answerForm})
    else:
        print(request.POST)
        answerForm = AnswerForm(request.POST)
        if answerForm.is_valid():
            print('--------',answerForm.cleaned_data)
            objs = []
            for key,v in answerForm.cleaned_data.items():
                k,qid = key.rsplit('_',1)
                answer_dict = {'student_id':user_id,'question_id':qid,k:v,'ctime':datetime.datetime.now()}
                objs.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(objs)
            return HttpResponse('感谢您的参与!!!')


        return render(request, "muban/answer.html", {'answerForm': answerForm})





def get_date_record(date):
    """
    获得某个日期的预定记录，根据会议室分组
    :param date: date字符串
    :return:
    """
    records = models.ReserveRecord.objects.filter(date=date)

    ret = defaultdict(list)
    for record in records:
        ret[record.meetingroom_id].append(record)
    return ret

def reserve_record(request):
    """
    某个日期的会议室预定记录
    :param request:
    :return:
    """
    select_date = request.GET.get('date',time.strftime('%Y-%m-%d', time.localtime(time.time())))
    print('---------',select_date)

    meetingroom_records = get_date_record(select_date)

    meetingroom_list = models.MeetingRoom.objects.all()
    record_list = models.ReserveRecord.objects.filter().all()
    reserve_phase = models.ReserveRecord.reserve_phase

    for x in meetingroom_records:
        print(x,meetingroom_records[x])

    name_dict = {
        'today':select_date,
        'meetingroom_list':meetingroom_list,
        'record_list':record_list,
        'reserve_phase':reserve_phase,
        'meetingroom_records':dict(meetingroom_records),
    }
    return render(request,'muban/reserve_record.html',name_dict)


def add_reserve(request):
    """
    添加预定记录
    :param request:
    :return:
    """
    # 模拟登陆
    pretend_login(request, "zihao", "123456a")
    user_id = request.session['userinfo']['id']
    date_str = request.POST.get('date')
    data = json.loads(request.POST.get('data'))
    print(date_str,user_id)
    objs = []
    for x in data:
        x['date'] = date_str
        x['user_id'] = user_id
        objs.append(models.ReserveRecord(**x))
    models.ReserveRecord.objects.bulk_create(objs)
    return HttpResponse(json.dumps("ok"))