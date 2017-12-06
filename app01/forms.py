from django.forms import Form,fields,ModelForm
from django.forms import widgets as wd
from app01 import models

class QuestionForm(Form):
    name = fields.CharField(
        required=True,  # 表示此项必填
        max_length=18,
        label="问题",
        label_suffix="：",
        error_messages={  # 出现错误时对应的提示信息
            'max_length': '问题名称不能超过18字',
            'required': '问题名称不能为空',
        },
        widget=wd.TextInput(
            attrs={'class':"dfinput question_name",'placeholder': '请输入问题名称'}
        )

    )

    type = fields.ChoiceField(
        choices=(),
        # initial=1,
        label="类型",
        label_suffix="：",
        widget=wd.Select(attrs={'class':"dfinput question_type"})
    )

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        self.fields['type'].widget.choices = models.Question.question_types
        if kwargs.get('initial'):
            self.fields['type'].initial = kwargs['initial']['type']
            self.fields['name'].widget.attrs['value'] = kwargs['initial']['value']


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields = ['name','score']
        labels = {
            'name':'内容',
            'score':'分值',
        }
        error_messages = {
            'name':{
                'required':'选项名称不能为空',
                'invalid':'选项名称类型错误',
            },
            'score': {
                'required': '选项值不能为空',
                'invalid': '选项值类型错误',
            }
        }

        widgets = {
            'name':wd.TextInput(
                attrs={
                    'class':'dfinput-sm option_value '
                }
            ),
            'score': wd.NumberInput(
                attrs={
                    'class': 'dfinput-sm option_key'
                }
            )
        }


class SurveyModelForm(ModelForm):
    class Meta:
        model = models.SurveyInfo
        fields = ['title', 'cls']

        labels = {
            'title': '问卷名称',
            'cls': '所属班级',
        }

        widgets = {
            'title':wd.TextInput(
                attrs={
                    'class':'dfinput'
                }
            ),
            'cls': wd.Select(
                attrs={
                    'class': 'dfinput'
                }
            )
        }
