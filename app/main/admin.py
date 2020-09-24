from django.contrib import admin
from main.models import *
# Register your models here.


# admin.site.register(Queue)
# admin.site.register(Statistic)
# admin.site.register(DistributingDevice)
# admin.site.register(Report)

admin.site.register(Statistic)
admin.site.register(MetricReport)
admin.site.register(Chaos)
admin.site.register(NetCompilationStat)
admin.site.register(DrawImgsReport)
admin.site.register(DrawImgsStat)
admin.site.register(NetCompileReport)

