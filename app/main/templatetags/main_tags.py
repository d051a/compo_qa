from django import template
from main.models import Chaos, DrawImgsReport, NetCompileReport

register = template.Library()


@register.filter(name='stats_view')
def stats_view(chaos_id):
    chaos = Chaos.objects.get(pk=chaos_id)
    draw_reports = DrawImgsReport.objects.filter(chaos=chaos)
    net_compile_reports = NetCompileReport.objects.filter(chaos=chaos)
    return f'net: {len(net_compile_reports)} draw: {len(draw_reports)}'
