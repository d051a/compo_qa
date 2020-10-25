from django import forms
from django.forms import ModelForm
from main.models import MetricReport, Chaos, DrawImgsReport, NetCompileReport


# class VersionForm(ModelForm):
#     class Meta:
#         model = Version
#         fields = [
#             'title',
#             'chaos',
#             'total_esl',
#             'shields_num',
#             'dd_nums',
#             'dd_configuration',
#             'dd_dongles_num',
#             'hardware_config',
#             'version_sum',
#             'version_chaos',
#             'chaos_configuration',
#             'tree_floor_num',
#             'version_driver',
#             'version_esl_firmware',
#             'version_esl_hw',
#             'version_dongles_hw',
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'total_esl': forms.TextInput(attrs={'class': 'form-control'}),
#             'shields_num': forms.TextInput(attrs={'class': 'form-control'}),
#             'dd_nums': forms.TextInput(attrs={'class': 'form-control'}),
#             'dd_configuration': forms.TextInput(attrs={'class': 'form-control'}),
#             'dd_dongles_num': forms.TextInput(attrs={'class': 'form-control'}),
#             'hardware_config': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_sum': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_chaos': forms.TextInput(attrs={'class': 'form-control'}),
#             'chaos_configuration': forms.TextInput(attrs={'class': 'form-control'}),
#             'tree_floor_num': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_driver': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_esl_firmware': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_esl_hw': forms.TextInput(attrs={'class': 'form-control'}),
#             'version_dongles_hw': forms.TextInput(attrs={'class': 'form-control'}),
#         }


class MetricReportForm(ModelForm):
    class Meta:
        model = MetricReport
        fields = ['chaos',
                  'net_compile_amount',
                  'draw_imgs_amount',
                  'fact_total_esl',
                  'draw_imgs_limit_mins',
                  'color',
                  'draw_imgs_type',
                  'net_compile_limit_mins',
                  'net_success_percent',
                  ]
        DRAW_IMGS_TYPE_CHOICES = (
            ('highlight', 'HighLight'),
            ('sum', 'СУМ')
        )
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'net_compile_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'draw_imgs_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_compile_limit_mins': forms.NumberInput(attrs={'class': 'form-control'}),
            'draw_imgs_limit_mins': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'draw_imgs_type': forms.Select(choices=DRAW_IMGS_TYPE_CHOICES, attrs={'class': 'form-control'}),
            'net_success_percent': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ChaosForm(ModelForm):
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


class ChaosEditForm(ChaosForm):
    class Meta:
        model = Chaos
        fields = ['name', 'ip', 'port', 'ssh_port', 'login',
                  'password', 'description', 'config', 'monitoring_config_params',
                  'multimeter_ip', 'bat_reserved', 'grafana_dashboard_url', 'dat_file', ]
        TRUE_FALSE_CHOICES = (
            (True, 'Да'),
            (False, 'Нет')
        )
        widgets = {
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.TextInput(attrs={'class': 'form-control'}),
            'ssh_port': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'config': forms.TextInput(attrs={'class': 'form-control'}),
            'monitoring_config_params': forms.TextInput(attrs={'class': 'form-control'}),
            'multimeter_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'bat_reserved': forms.Select(choices=TRUE_FALSE_CHOICES, attrs={'class': 'form-control'}),
            'dat_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'grafana_dashboard_url': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DrawImgsReportForm(ModelForm):
    class Meta:
        model = DrawImgsReport
        fields = ['chaos',
                  'metric_report',
                  'fact_total_esl',
                  'draw_imgs_limit_mins',
                  'color',
                  'draw_imgs_type'
                  ]
        DRAW_IMGS_TYPE_CHOICES = (
            ('highlight', 'HighLight'),
            ('sum', 'СУМ')
        )
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.TextInput(attrs={'class': 'form-control'}),
            'draw_imgs_limit_mins': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'metric_report': forms.HiddenInput(),
            'draw_imgs_type': forms.Select(choices=DRAW_IMGS_TYPE_CHOICES, attrs={'class': 'form-control'})
        }


class NetCompileReportForm(ModelForm):
    class Meta:
        model = NetCompileReport
        fields = ['chaos',
                  'metric_report',
                  'fact_total_esl',
                  'net_compile_limit_mins',
                  'success_percent',
                  ]
        widgets = {
            'chaos': forms.Select(attrs={'class': 'form-control'}),
            'fact_total_esl': forms.TextInput(attrs={'class': 'form-control'}),
            'net_compile_limit_mins': forms.TextInput(attrs={'class': 'form-control'}),
            'metric_report': forms.HiddenInput(),
            'success_percent': forms.NumberInput(attrs={'class': 'form-control'}),
        }
