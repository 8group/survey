from django.db import models

# Create your models here.
class Cls(models.Model):
    """
    班级表
    """
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class UserInfo(models.Model):
    """
    员工表
    """
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    cls = models.ForeignKey(to=Cls)

    def __str__(self):
        return self.username


class SurveyInfo(models.Model):
    """
    问卷表
    """
    title = models.CharField(max_length=64)
    cls = models.ForeignKey(to=Cls)
    creator = models.ForeignKey(to=UserInfo)

    def __str__(self):
        return self.title



class Question(models.Model):
    """
    问题
    """
    name = models.CharField(max_length=64)
    surveyinfo = models.ForeignKey(to=SurveyInfo)
    question_types = (
        (1,'打分'),
        (2,'单选'),
        (3,'评价'),
    )
    type = models.IntegerField(choices=question_types)

    def __str__(self):
        return self.name

class Option(models.Model):
    """
    单选题的选项
    """
    name = models.CharField(verbose_name='选项名称',max_length=32)
    score = models.IntegerField(verbose_name='选项对应的分值')
    question = models.ForeignKey(to=Question)

    def __str__(self):
        return self.name

class Answer(models.Model):
    """
    回答
    """
    student = models.ForeignKey(to=UserInfo)
    question = models.ForeignKey(to=Question)
    ctime = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return self.name
