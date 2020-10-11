import json
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from main.models import Statistic, MetricReport, Chaos, DrawImgsReport, NetCompileReport
from main.chaos_utils import Utils as utils
from django.views.generic import DetailView, CreateView, ListView, UpdateView
from django.urls import reverse_lazy, reverse
from main.forms import ChaosForm, DrawImgsReportForm, NetCompileReportForm, MetricReportForm, ChaosEditForm
from main.tasks.tasks import drawed_images_report_generate, net_compilation, all_metrics_report_generate


def main(request):
    return redirect('/chaoses/')


def metrics_list(request):
    return render(request, 'main/metrics_report_list.html', {
        'pagename': 'Метрики'
    })


def net_compiles_list(request):
    return render(request, 'main/net_compiles_list.html', {
        'pagename': 'Сборки сети'
    })


def draw_imgs_list(request):
    return render(request, 'main/draw_imgs_list.html', {
        'pagename': 'Отрисовки ценников'
    })


def chaoses_list(request):
    return render(request, 'main/chaoses_list.html', {
        'pagename': 'Chaoses'
    })


def get_chaos_config(request, pk):
    chaos = Chaos.objects.get(pk=pk)
    chaos_credentials = {'ip': chaos.ip,
                         'login': chaos.login,
                         'password': chaos.password,
                         'port': chaos.ssh_port
                         }
    config_data = utils.run_remote_command(chaos_credentials['ip'],
                                          chaos_credentials['login'],
                                          chaos_credentials['password'],
                                          chaos_credentials['port'],
                                          f'cat /var/Componentality/Chaos/chaos_config.json'
                                          )
    if config_data is None:
        chaos.config = ''
        chaos.save()
    config_json = json.loads(config_data[0])
    chaos.config = config_json
    chaos.save()
    return HttpResponseRedirect(reverse('main:chaos_edit', args=(pk,)))


class ChaosCreate(CreateView):
    model = Chaos
    context_object_name = 'Новое РУ'
    form_class = ChaosForm
    template_name = 'main/chaos_add.html'
    success_url = reverse_lazy('main:chaoses_list')


class ChaosEdit(UpdateView):
    model = Chaos
    context_object_name = 'Изменение настроек Хаоса'
    form_class = ChaosEditForm
    template_name = 'main/chaos_edit.html'
    success_url = reverse_lazy('main:chaoses_list')


class ChaosDetail(DetailView):
    model = Chaos
    context_object_name = 'Хаос информация'
    template_name = 'main/chaos_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chaos = context['object']
        try:
            current_stats = Statistic.objects.filter(chaos=chaos)[0]
            stats_string = [
                f"<b>{str(field).split('.')[2]}</b>: {getattr(current_stats, str(field).split('.')[2])}<br>"
                for field in current_stats._meta.get_fields()[1:]
            ]
        except:
            stats_string = 'нет данных'
        context['chaos_pk'] = int(self.kwargs['pk'])
        context['current_stats'] = ''.join(stats_string)
        return context


class ChaosStats(DetailView):
    model = Chaos
    context_object_name = 'Хаос статистика'
    template_name = 'main/chaos_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chaos = context['object']
        context['chaos_pk'] = chaos.pk
        return context


class ChaosListView(ListView):
    permission_required = 'ticketsapp.can_view_imperformer_ticketslist'
    template_name = 'main/chaoses_list.html'
    model = Chaos
    context_object_name = 'chaoses'


class MetricReportCreate(CreateView):
    model = MetricReport
    context_object_name = 'Новый сбор метрик'
    form_class = MetricReportForm
    template_name = 'main/metric_report_add.html'
    success_url = reverse_lazy('main:metrics_list')

    def form_valid(self, form):
        form.save()
        task = all_metrics_report_generate.delay(form.instance.id)
        redirect_url = super().form_valid(form)
        metric_report = MetricReport.objects.get(pk=form.instance.id)
        metric_report.task_id = task.id
        metric_report.save()
        return redirect_url


class MetricReportDetail(DetailView):
    model = MetricReport
    context_object_name = 'Отчет'
    template_name = 'main/metric_report_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = context['object']
        context['chaos_pk'] = report.chaos.pk
        return context


class NetCompileReportDetail(DetailView):
    model = NetCompileReport
    context_object_name = 'Отрисованные ценники'
    template_name = 'main/net_compiles_report_detail.html'


class DrawImgsReportDetail(DetailView):
    model = DrawImgsReport
    context_object_name = 'Отрисованные ценники'
    template_name = 'main/draw_imgs_report_detail.html'


class DrawImgsReportCreate(CreateView):
    model = DrawImgsReport
    context_object_name = 'Новая отрисовка сети'
    form_class = DrawImgsReportForm
    template_name = 'main/draw_imgs_add.html'
    success_url = reverse_lazy('main:drawed_list')

    def form_valid(self, form):
        form.save()
        task = drawed_images_report_generate.delay(form.instance.id)
        redirect_url = super().form_valid(form)
        draw_imgs_report = DrawImgsReport.objects.get(pk=form.instance.id)
        draw_imgs_report.task_id = task.id
        draw_imgs_report.save()
        return redirect_url


class NetCompiliesReportCreate(CreateView):
    model = NetCompileReport
    context_object_name = 'Новая отрисовка сети'
    form_class = NetCompileReportForm
    template_name = 'main/net_compiles_add.html'
    success_url = reverse_lazy('main:net_compiles_list')

    def form_valid(self, form):
        form.save()
        net_compilation.delay(form.instance.id)
        task = net_compilation.delay(form.instance.id)
        redirect_url = super().form_valid(form)
        net_compilation_report = NetCompileReport.objects.get(pk=form.instance.id)
        net_compilation_report.task_id = task.id
        net_compilation_report.save()
        return redirect_url
