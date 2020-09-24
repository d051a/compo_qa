from main.models import Statistic, \
    MetricReport, NetCompilationStat, DrawImgsStat, DrawImgsReport, NetCompileReport
from django_datatables_view.base_datatable_view import BaseDatatableView
from main.chaos_utils import Utils as utils


class FilterQuerysetMixin(BaseDatatableView):
    def filter_queryset(self, queryset):
        report_id = self.request.GET.get('report_pk', None)
        chaos_id = self.request.GET.get('chaos_pk', None)
        if report_id:
            report = MetricReport.objects.get(pk=report_id)
            queryset = queryset.filter(metric_report=report)
        if chaos_id:
            queryset = queryset.filter(chaos=chaos_id)
        return queryset


class DrawImgsReportModelListJson(FilterQuerysetMixin, BaseDatatableView):
    model = DrawImgsReport
    columns = ['pk', 'create_date_time', 'status', 'date_time_finish', 'name', 'ip', 'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100']

    def render_column(self, row, column):
        if column == 'pk':
            return f'<a href="/drawed/{row.pk}">Отрисовка ценников #{row.pk}</a>'
        if column == 'name':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.name}</a>'
            except:
                return ''
        if column == 'ip':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.ip}</a>'
            except:
                return ''
        if column == 'create_date_time':
            return row.create_date_time.strftime("%d.%m.%y %H:%M:%S")
        if column == 'date_time_finish':
            if row.date_time_finish:
                return row.date_time_finish.strftime("%d.%m.%y %H:%M:%S")
            else:
                return ''
        else:
            return super(DrawImgsReportModelListJson, self).render_column(row, column)


class ChaosStatisticModelListJson(FilterQuerysetMixin, BaseDatatableView):
    model = Statistic
    columns = ['date_time',
               'total_nodes',
               'inaccessible_nodes',
               'total_number_routes',
               'maximum_road_length',
               'average_route_length',
               'accessible_nodes_percent',
               'elapsed_time',
               'total_esl',
               'online_esl',
               'images_in_transit',
               'images_in_draw',
               'images_in_resend_queue',
               'images_succeeded',
               'images_failed',
               'currently_scanning',
               'network_mode',
               'connects',
               ]

    def render_column(self, row, column):
        if column == 'date_time':
            return row.date_time.strftime("%d.%m.%y %H:%M:%S")
        else:
            return super(ChaosStatisticModelListJson, self).render_column(row, column)


class NetCompilationReportModelListJson(FilterQuerysetMixin, BaseDatatableView):
    model = NetCompileReport
    columns = ['pk', 'create_date_time', 'status', 'date_time_finish', 'name', 'ip', 'p50', 'p75', 'p90', 'p95', 'p96',     'p97', 'p98', 'p99', 'p100']

    def render_column(self, row, column):
        if column == 'pk':
            return f'<a href="/netcompiles/{row.pk}">Сборка сети #{row.pk}</a>'
        if column == 'name':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.name}</a>'
            except:
                return ''
        if column == 'ip':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.ip}</a>'
            except:
                return ''
        if column == 'create_date_time':
            return row.create_date_time.strftime("%d.%m.%y %H:%M:%S")
        if column == 'date_time_finish':
            if row.date_time_finish:
                return row.date_time_finish.strftime("%d.%m.%y %H:%M:%S")
            else:
                return ''
        else:
            return super(NetCompilationReportModelListJson, self).render_column(row, column)


class DrawImgsStatModelListJson(BaseDatatableView):
    model = DrawImgsStat
    columns = ['percent_step',
               'images_succeeded',
               'elapsed_time',
               ]

    def render_column(self, row, column):
        return super(DrawImgsStatModelListJson, self).render_column(row, column)

    def filter_queryset(self, queryset):
        report_id = self.request.GET.get('report_pk', None)
        report = DrawImgsReport.objects.get(pk=report_id)
        if report_id:
            queryset = queryset.filter(draw_imgs_report=report)
        return queryset


class NetCompilationStatModelListJson(BaseDatatableView):
    model = NetCompilationStat
    columns = ['elapsed_time',
               'online_esl',
               'compilation_percent',
               ]

    def render_column(self, row, column):
        return super(NetCompilationStatModelListJson, self).render_column(row, column)

    def filter_queryset(self, queryset):
        report_id = self.request.GET.get('report_pk', None)
        chaos_id = self.request.GET.get('chaos_pk', None)
        if report_id:
            report = NetCompileReport.objects.get(pk=report_id)
            queryset = queryset.filter(net_compile_report=report)
        if chaos_id:
            queryset = queryset.filter(chaos=chaos_id)
            print(queryset)
        return queryset


class MetricsModelListJson(BaseDatatableView):
    model = MetricReport
    columns = ['pk', 'create_date_time', 'date_time_finish', 'status', 'elapsed_time', 'name', 'ip']

    def render_column(self, row, column):
        if column == 'pk':
            return f'<a href="/metrics/{row.pk}">Общий отчет #{row.pk}</a>'
        if column == 'name':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.name}</a>'
            except:
                return ''
        if column == 'ip':
            try:
                return f'<a href="/chaoses/{row.chaos.pk}">{row.chaos.ip}</a>'
            except:
                return ''
        if column == 'create_date_time':
            return row.create_date_time.strftime("%d.%m.%y %H:%M:%S")
        if column == 'date_time_finish':
            if row.date_time_finish:
                return row.date_time_finish.strftime("%d.%m.%y %H:%M:%S")
            else:
                return ''
        if column == 'elapsed_time':
            if row.date_time_finish:

                elapsed_time = utils.get_time_delta(row.date_time_finish, row.create_date_time, "{hours}:{minutes}:{seconds}")
                return elapsed_time
            else:
                return ''
        else:
            return super(MetricsModelListJson, self).render_column(row, column)

    def filter_queryset(self, queryset):
        chaos_id = self.request.GET.get('chaos_pk', None)
        if chaos_id:
            queryset = queryset.filter(chaos=chaos_id)
        return queryset

