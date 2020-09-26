from . import views, views_dbs, views_excel
from django.urls import path


app_name = 'main'

urlpatterns = [
    path('', views.main, name='main'),
    path('chaoses/', views.ChaosListView.as_view(), name='chaoses_list'),
    path('chaoses/add/', views.ChaosCreate.as_view(), name='chaos_add'),
    path('chaoses/<int:pk>/', views.ChaosDetail.as_view(), name='chaos_detail'),
    path('chaoses/<int:pk>/stats', views.ChaosStats.as_view(), name='chaos_stats'),
    path('metrics/', views.metrics_list, name='metrics_list'),
    path('metrics/<int:pk>/', views.MetricReportDetail.as_view(), name='metrics_detail'),
    path('metrics/add', views.MetricReportCreate.as_view(), name='metrics_add'),
    path('drawed/', views.draw_imgs_list, name='drawed_list'),
    path('drawed/<int:pk>/', views.DrawImgsReportDetail.as_view(), name='drawed_detail'),
    path('drawed/add', views.DrawImgsReportCreate.as_view(), name='draw_imgs_add'),
    path('netcompiles/', views.net_compiles_list, name='net_compiles_list'),
    path('netcompiles/<int:pk>/', views.NetCompileReportDetail.as_view(), name='net_compiles_detail'),
    path('netcompiles/add', views.NetCompiliesReportCreate.as_view(), name='net_compiles_add'),

    # excel reports generators
    path('metrics/<int:chaos_id>/stats/excel', views_excel.chaos_stats_export_to_xlsx, name='chaos_stats_export_to_xlsx'),
    path('metrics/<int:metric_report_id>/excel', views_excel.metric_report_export_to_xlsx, name='export_report_data_to_xlsx'),

    # excel json-datatables
    path('metric_reports_list_json/', views_dbs.MetricsModelListJson.as_view(), name='metric_reports_list_json'),
    path('chaos_stats_json/', views_dbs.ChaosStatisticModelListJson.as_view(), name='chaos_stats_json'),
    path('drawed_imgs_reports_json/', views_dbs.DrawImgsReportModelListJson.as_view(), name='drawed_imgs_reports_json'),
    path('drawed_imgs_stats_json/', views_dbs.DrawImgsStatModelListJson.as_view(), name='drawed_imgs_stats_json'),
    path('net_compile_stats_json/', views_dbs.NetCompilationStatModelListJson.as_view(), name='net_compile_stats_json'),
    path('net_compile_list_json/', views_dbs.NetCompilationReportModelListJson.as_view(), name='net_compile_list_json'),

    path('chaoses/<int:pk>/get_config/', views.get_chaos_config, name='get_chaos_config'),


]
