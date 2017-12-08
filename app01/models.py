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
    creator = models.ForeignKey(to=UserInfo,null=True,blank=True)

    def __str__(self):
        return self.title



class Question(models.Model):
    """
    问题
    """
    name = models.CharField(max_length=64)
    surveyinfo = models.ForeignKey(to=SurveyInfo)
    question_types = (
        (1, '打分（1~10分）'),
        (2, '单选'),
        (3, '评论'),
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
    content = models.CharField(max_length=255,null=True,blank=True,verbose_name='文本答案')
    val = models.IntegerField(null=True,blank=True,verbose_name='打分答案')
    option = models.ForeignKey(to=Option,null=True,blank=True,verbose_name='单选答案')

    def __str__(self):
        return "".join([self.student.username,self.question.name])


class MeetingRoom(models.Model):
    """
    会议室
    """
    name = models.CharField(verbose_name='会议室名称',max_length=32)


class ReserveRecord(models.Model):
    """
    预定记录
    """
    meetingroom = models.ForeignKey(to=MeetingRoom,verbose_name='会议室')
    user = models.ForeignKey(to=UserInfo,verbose_name='使用人')
    date = models.DateField()
    reserve_phase = (
        (1, '8:00'),
        (2, '9:00'),
        (3, '10:00'),
        (4, '11:00'),
        (5, '12:00'),
        (6, '13:00'),
        (7, '14:00'),
        (8, '15:00'),
        (9, '16:00'),
        (10, '17:00'),
        (11, '18:00'),
        (12, '19:00'),
    )
    phase = models.IntegerField(choices=reserve_phase,verbose_name='使用阶段')

    class Meta:
        unique_together = ('meetingroom', 'date', 'phase')