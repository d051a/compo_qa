from django import forms
from django.forms import ModelForm
from main.models import MetricReport, Chaos, DrawImgsReport, NetCompileReport


class MetricReportForm(ModelForm):
    class Meta:
        model = MetricReport
        fields = ['chaos',
                  'net_compile_amount',
                  'draw_imgs_amount',
                  'fact_total_esl',
                  'draw_imgs_limit_mins',
                  'net_compile_limit_mins'
                  ]
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'net_compile_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'draw_imgs_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_compile_limit_mins': forms.NumberInput(attrs={'class': 'form-control'}),
            'draw_imgs_limit_mins': forms.NumberInput(attrs={'class': 'form-control'}),

        }


class ChaosForm (ModelForm):
    class Meta:
        model = Chaos
        fields = ['name', 'ip', 'port', 'ssh_port', 'login', 'password', 'description']
        widgets = {
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.TextInput(attrs={'class': 'form-control'}),
            'ssh_port': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DrawImgsReportForm(ModelForm):
    class Meta:
        model = DrawImgsReport
        fields = ['chaos',
                  'metric_report',
                  'fact_total_esl',
                  'draw_imgs_limit_mins',
                  # 'draw_imgs_amount'
                  ]
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.TextInput(attrs={'class': 'form-control'}),
            'draw_imgs_limit_mins': forms.TextInput(attrs={'class': 'form-control'}),
            # 'draw_imgs_amount': forms.TextInput(attrs={'class': 'form-control'}),
            'metric_report': forms.HiddenInput(),
        }


class NetCompileReportForm(ModelForm):
    class Meta:
        model = NetCompileReport
        fields = ['chaos',
                  'metric_report',
                  'fact_total_esl',
                  'net_compile_limit_mins',
                  # 'net_compile_amount',
                  ]
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.TextInput(attrs={'class': 'form-control'}),
            'net_compile_limit_mins': forms.TextInput(attrs={'class': 'form-control'}),
            # 'net_compile_amount': forms.TextInput(attrs={'class': 'form-control'}),
            'metric_report': forms.HiddenInput(),
        }
