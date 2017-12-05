from django.forms import Form,fields,widgets
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
        widget=widgets.TextInput(
            attrs={'class':"dfinput question_name",'placeholder': '请输入问题名称'}
        )

    )

    type = fields.ChoiceField(
        choices=(),
        # initial=1,
        label="类型",
        label_suffix="：",
        widget=widgets.Select(attrs={'class':"dfinput question_type"})
    )

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        self.fields['type'].widget.choices = models.Question.question_types
        self.fields['type'].initial = kwargs['initial']['type']
        self.fields['name'].widget.attrs['value'] = kwargs['initial']['value']


