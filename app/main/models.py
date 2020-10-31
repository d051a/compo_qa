from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Version(models.Model):
    version_num = models.CharField('Номер версии', max_length=30, unique=True, null=True)
    date_time = models.DateTimeField('Дата и время создания',
                                     default=timezone.localtime, blank=True, null=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Версия"
        verbose_name_plural = "Версии"

    def __str__(self):
        return self.version_num


class Configuration(models.Model):
    date_time = models.DateTimeField('Дата и время создания',
                                     default=timezone.localtime, blank=True, null=True)
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Стенд', null=True)
    metric_report = models.OneToOneField('MetricReport',
                                         on_delete=models.CASCADE, verbose_name='Общий отчет',
                                         null=True, blank=True)
    netcompile_report = models.OneToOneField('NetCompileReport',
                                             on_delete=models.CASCADE, verbose_name='Отчет о сборке сети',
                                             null=True, blank=True)
    drawimgs_report = models.OneToOneField('DrawImgsReport',
                                           on_delete=models.CASCADE, verbose_name='Отчет об отрисовке',
                                           null=True, blank=True)
    version_num = models.ForeignKey('Version', on_delete=models.CASCADE, verbose_name='Версия', null=True)
    shields_num = models.CharField('Номера щитов', max_length=50, blank=True, null=True)
    hardware_config = models.CharField('Конфигурация системы', max_length=400, blank=True, null=True)
    total_esl = models.IntegerField('Количество ценников стенда, шт', blank=True, null=True)
    dd_nums = models.CharField('Количество РУ, шт', max_length=350, blank=True, null=True)
    dd_configuration = models.CharField('Конфигурация РУ', max_length=350, blank=True, null=True)
    dd_dongles_num = models.CharField('Количество донглов на РУ, шт', max_length=150, blank=True, null=True)
    version_sum = models.CharField('Версия СУМ', max_length=30, blank=True, null=True)
    version_chaos = models.CharField('Версия Хаоса', max_length=30, blank=True, null=True)
    chaos_configuration = models.TextField('Конфигурация Хаоса', blank=True, null=True)
    tree_floor_num = models.IntegerField('Число этажей дерева', blank=True, null=True)
    version_driver = models.CharField('Версия драйвера', max_length=30, blank=True, null=True)
    version_esl_firmware = models.CharField('Версия прошивки ЭЦ', max_length=250, blank=True, null=True)
    version_esl_hw = models.CharField('HW версия ЭЦ', max_length=250, blank=True, null=True)
    version_dongles_hw = models.CharField('HW версия донглов', max_length=250, blank=True, null=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Конфигурация"
        verbose_name_plural = "Конфигурации"

    def __str__(self):
        report_title = ''
        if self.netcompile_report:
            report_title = f'сборки сети #{self.netcompile_report.pk}'
        if self.drawimgs_report:
            report_title = f'отрисовки ценников #{self.drawimgs_report.pk}'
        # if self.metric_report:
        #     report_title = f'общего отчета #{self.metric_report.pk}'
        full_title_string = f"Конфигурация {self.version_num if self.version_num else ''} " \
            f"{report_title}{'общий отчет #' + str(self.metric_report.pk) if self.metric_report else ''} для {self.chaos.name}"
        return full_title_string


class Statistic(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True)
    metric_report = models.ForeignKey('MetricReport', on_delete=models.CASCADE, verbose_name='Отчет метрик', null=True)
    total_nodes = models.IntegerField('total_nodes', null=True)
    inaccessible_nodes = models.IntegerField('inaccessible_nodes', null=True)
    total_number_routes = models.IntegerField('total_number_routes', null=True)
    maximum_road_length = models.IntegerField('maximum_road_length', null=True)
    average_route_length = models.FloatField('average_route_length', null=True)
    accessible_nodes_percent = models.FloatField('accessible_nodes_percent', null=True)
    elapsed_time = models.FloatField('elapsed_time', null=True)
    total_esl = models.IntegerField('total_esl', null=True)
    online_esl = models.IntegerField('online_esl', null=True)
    images_in_transit = models.IntegerField('images_in_transit', null=True)
    images_in_draw = models.IntegerField('images_in_draw', null=True)
    images_in_resend_queue = models.IntegerField('images_in_resend_queue', null=True)
    images_succeeded = models.IntegerField('images_succeeded', null=True)
    images_failed = models.IntegerField('images_failed', null=True)
    currently_scanning = models.IntegerField('currently_scanning', null=True)
    network_mode = models.CharField('network_mode', max_length=100, null=True)
    network_mode_percent = models.IntegerField('network_mode_percent', null=True)
    connects = models.IntegerField('connects', null=True)
    date_time = models.DateTimeField('Дата и время', default=timezone.localtime, blank=True, null=True)
    voltage_current = models.FloatField('Текущий вольтаж', blank=True, null=True)
    voltage_average = models.FloatField('Средний вольтаж', blank=True, null=True)
    voltage_max = models.FloatField('Максимальный вольтаж', blank=True, null=True)
    bat_reserved1 = models.IntegerField('bat_reserved1', blank=True, null=True)
    bat_reserved2 = models.IntegerField('bat_reserved2', blank=True, null=True)
    bat_reserved3 = models.IntegerField('bat_reserved3', blank=True, null=True)
    bat_reserved4 = models.IntegerField('bat_reserved4', blank=True, null=True)

    class Meta:
        ordering = ["-date_time"]
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"

    def __str__(self):
        return f'{self.date_time}'


class Chaos(models.Model):
    name = models.CharField('Имя сервера', max_length=50)
    ip = models.GenericIPAddressField('IP-адрес', protocol='IPv4', unpack_ipv4=False)
    port = models.CharField('Порт Хаоса', max_length=6, default=19872)
    ssh_port = models.CharField('Порт ssh', max_length=6, default=22)
    login = models.CharField('Логин', max_length=50, default='pi')
    password = models.CharField('Пароль', max_length=100, default='CompoM123')
    status = models.CharField('Статус', max_length=50, blank=True, null=True)
    description = models.CharField('Описание', max_length=200, blank=True, null=True)
    esl_total = models.CharField('ESL (всего)', max_length=20, blank=True, null=True)
    images_succeeded = models.CharField('Images succeeded', max_length=20, blank=True, null=True)
    net_percent = models.CharField('Сборка сети (%)', max_length=50, blank=True, null=True)
    draw_percent = models.CharField('Отрисовка (%)', max_length=50, blank=True, null=True)
    date_time_update = models.DateTimeField('Время обновления данных',
                                            default=timezone.localtime, blank=True, null=True)
    config = models.TextField('Текущий конфиг хаоса', blank=True, null=True)
    monitoring_config_params = models.TextField('Отслеживаемые поля конфига', blank=True, null=True)
    compired_config = models.TextField('Результат сравнения конфигов', blank=True, null=True)
    compired_config_date = models.DateTimeField('Дата и время сравнения конфигов', blank=True, null=True)
    compired_config_errs = models.IntegerField('Расхождений в сравниваемых параметрах конфигов',
                                               default=0, blank=True, null=True)
    compired_config_warns = models.IntegerField('Расхождений в параметрах конфигов', default=0, blank=True, null=True)
    multimeter_ip = models.GenericIPAddressField('IP-адрес мультиметра',
                                                 protocol='IPv4', unpack_ipv4=False, blank=True, null=True)
    bat_reserved = models.BooleanField('Отслеживать bat_reserved', default=False, blank=True, null=True)
    dat_file = models.FileField('.dat файл выгрузки товаров и цен', blank=True, null=True)
    grafana_dashboard_url = models.CharField('URL дашборда в Grafana', max_length=200, blank=True, null=True)
    shields_num = models.CharField('Номера щитов', max_length=50, blank=True, null=True)
    hardware_config = models.CharField('Конфигурация системы', max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Хаос"
        verbose_name_plural = "Хаосы"

    def __str__(self):
        return f'{self.name} - {self.ip}'


class NetCompilationStat(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True, blank=True)
    net_compile_report = models.ForeignKey('NetCompileReport',
                                           on_delete=models.CASCADE,
                                           verbose_name='NetCompileReport',
                                           null=True,
                                           blank=True)
    online_esl = models.IntegerField('Ценников онлайн')
    compilation_percent = models.FloatField('Компиляция сети (%)')
    elapsed_time = models.CharField('Затраченное время', max_length=50)
    date_time = models.DateTimeField('Дата и время записи',
                                     default=timezone.localtime, blank=True, null=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Сборка сети"
        verbose_name_plural = "Сборки сети"

    def __str__(self):
        return f'Сборка сети #{self.pk} отчета #{self.net_compile_report}'


class NetCompileReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True)
    metric_report = models.ForeignKey('MetricReport',
                                      on_delete=models.CASCADE,
                                      verbose_name='Отчет сбора метрик',
                                      null=True,
                                      blank=True)
    create_date_time = models.DateTimeField('Дата и время начала сборки',
                                            default=timezone.localtime, blank=True, null=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    net_compile_limit_mins = models.IntegerField('Предельное время сборки сети(мин)',
                                                 default=120, blank=True, null=True)
    net_compile_amount = models.IntegerField('Количество сборок сети', default=1, blank=True, null=True)
    date_time_finish = models.DateTimeField('Дата и время окончания сборки', null=True, blank=True)
    fact_total_esl = models.IntegerField('Фактическое количество ESL', null=True, blank=True)
    p10 = models.CharField('Время сборки 10%', max_length=100, blank=True)
    p20 = models.CharField('Время сборки 20%', max_length=100, blank=True)
    p30 = models.CharField('Время сборки 30%', max_length=100, blank=True)
    p40 = models.CharField('Время сборки 40%', max_length=100, blank=True)
    p50 = models.CharField('Время сборки 50%', max_length=100, blank=True)
    p60 = models.CharField('Время сборки 60%', max_length=100, blank=True)
    p75 = models.CharField('Время сборки 75%', max_length=100, blank=True)
    p90 = models.CharField('Время сборки 90%', max_length=100, blank=True)
    p95 = models.CharField('Время сборки 95%', max_length=100, blank=True)
    p96 = models.CharField('Время сборки 96%', max_length=100, blank=True)
    p97 = models.CharField('Время сборки 97%', max_length=100, blank=True)
    p98 = models.CharField('Время сборки 98%', max_length=100, blank=True)
    p99 = models.CharField('Время сборки 99%', max_length=100, blank=True)
    p995 = models.CharField('Время сборки 99.5%', max_length=100, blank=True)
    p999 = models.CharField('Время сборки 99.9%', max_length=100, blank=True)
    p100 = models.CharField('Время сборки 100%', max_length=100, blank=True)
    t10 = models.CharField('Собранность сети за 10 мин., %', max_length=100, blank=True)
    t20 = models.CharField('Собранность сети за 20 мин., %', max_length=100, blank=True)
    t30 = models.CharField('Собранность сети за 30 мин., %', max_length=100, blank=True)
    t40 = models.CharField('Собранность сети за 40 мин., %', max_length=100, blank=True)
    t50 = models.CharField('Собранность сети за 50 мин., %', max_length=100, blank=True)
    t60 = models.CharField('Собранность сети за 60 мин., %', max_length=100, blank=True)
    t70 = models.CharField('Собранность сети за 70 мин., %', max_length=100, blank=True)
    t80 = models.CharField('Собранность сети за 80 мин., %', max_length=100, blank=True)
    t90 = models.CharField('Собранность сети за 90 мин., %', max_length=100, blank=True)
    t100 = models.CharField('Собранность сети за 100 мин., %', max_length=100, blank=True)
    t110 = models.CharField('Собранность сети за 110 мин., %', max_length=100, blank=True)
    t120 = models.CharField('Собранность сети за 120 мин., %', max_length=100, blank=True)
    t130 = models.CharField('Собранность сети за 130 мин., %', max_length=100, blank=True)
    t140 = models.CharField('Собранность сети за 140 мин., %', max_length=100, blank=True)
    t150 = models.CharField('Собранность сети за 150 мин., %', max_length=100, blank=True)
    final_percent = models.FloatField('Процент сборки сети', blank=True, null=True)
    elapsed_time = models.CharField('Время сборки сети', max_length=100, blank=True, null=True)
    max_inactive_time = models.IntegerField('Предельное время бездействия', default=30, blank=True, null=True)
    success_percent = models.FloatField('Считать сборку успешной при, %', default=100, blank=True, null=True)
    task_id = models.CharField('Celery task ID', max_length=200, blank=True, null=True)
    config = models.OneToOneField('Configuration',
                                  on_delete=models.CASCADE, verbose_name='Конфигурация',
                                  null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Отчет сборки сети"
        verbose_name_plural = "Сборки сети ОТЧЕТЫ"

    def __str__(self):
        return f'Отчет сборки сети #{self.pk}'


class MetricReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True)
    create_date_time = models.DateTimeField('Дата и время начала сбора статистики',
                                            default=timezone.localtime, blank=True, null=True)
    net_compile_limit_mins = models.IntegerField('Предельное время сборки сети(мин)',
                                                 default=120, blank=True, null=True)
    draw_imgs_limit_mins = models.IntegerField('Предельное время отрисовки ценников (мин)',
                                               default=300, blank=True, null=True)
    net_compile_amount = models.IntegerField('Количество сборок сети', default=1, blank=True, null=True)
    draw_imgs_amount = models.IntegerField('Количество отрисовок', default=1, blank=True, null=True)
    fact_total_esl = models.IntegerField('Фактическое количество ESL онлайн', null=True, blank=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    date_time_finish = models.DateTimeField('Дата и время окончания сбора статистики', null=True, blank=True)
    color = models.CharField('Цвет отрисовки',
                             max_length=3,
                             default='RBW',
                             blank=True,
                             validators=[RegexValidator(regex='^[WBR]{3}$',
                                                        message='Длина строки должна равняться любым 3 символам: R,B,W',
                                                        code='nomatch')],)
    net_inactive_time = models.IntegerField('Предельное время бездействия сборки сети',
                                            default=30, blank=True, null=True)
    draw_inactive_time = models.IntegerField('Предельное время бездействия отрисовки',
                                             default=30, blank=True, null=True)
    net_success_percent = models.FloatField('Считать сборку сети успешной при, %', default=100.0, blank=True, null=True)
    draw_success_percent = models.FloatField('Считать отрисовку успешной при, %', default=100.0, blank=True, null=True)
    task_id = models.CharField('Celery task ID', max_length=200, blank=True, null=True)
    draw_imgs_type = models.CharField('Тип отрисовки ценников', max_length=20, blank=True, null=True)
    config = models.OneToOneField('Configuration',
                                  on_delete=models.CASCADE, verbose_name='Конфигурация',
                                  null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Метрика Хаоса"
        verbose_name_plural = "Метрики Хаоса"

    def __str__(self):
        return f'Метрика хаоса #{self.pk}'


class DrawImgsReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True)
    metric_report = models.ForeignKey('MetricReport',
                                      on_delete=models.CASCADE,
                                      verbose_name='Отчет сбора метрик',
                                      null=True,
                                      blank=True)
    create_date_time = models.DateTimeField('Дата и время создания отчета',
                                            default=timezone.localtime, blank=True, null=True)
    date_time_finish = models.DateTimeField('Дата и время окончания отчета', blank=True, null=True)
    draw_imgs_limit_mins = models.IntegerField('Предельное время отрисовки ценников (мин)',
                                               default=300, blank=True, null=True)
    draw_imgs_amount = models.IntegerField('Количнство отрисовок ценников', default=1, blank=True, null=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    fact_total_esl = models.IntegerField('Фактическое количество ESL онлайн', null=True, blank=True)
    drawed_esl = models.IntegerField('Отрисовано ценников, шт', null=True, blank=True)
    not_drawed_esl = models.IntegerField('Не отрисовано, шт ', null=True, blank=True)
    color = models.CharField('Цвет отрисовки',
                             max_length=3,
                             default='RBW',
                             blank=True,
                             validators=[RegexValidator(regex='^[WBR]{3}$',
                                                        message='Длина строки должна равняться любым 3 символам: R,B,W',
                                                        code='nomatch')],)
    p10 = models.CharField('Время отрисовки 10%', max_length=100, blank=True)
    p20 = models.CharField('Время отрисовки 20%', max_length=100, blank=True)
    p30 = models.CharField('Время отрисовки 30%', max_length=100, blank=True)
    p40 = models.CharField('Время отрисовки 40%', max_length=100, blank=True)
    p50 = models.CharField('Время отрисовки 50%', max_length=100, blank=True)
    p60 = models.CharField('Время отрисовки 60%', max_length=100, blank=True)
    p75 = models.CharField('Время отрисовки 75%', max_length=100, blank=True)
    p90 = models.CharField('Время отрисовки 90%', max_length=100, blank=True)
    p95 = models.CharField('Время отрисовки 95%', max_length=100, blank=True)
    p96 = models.CharField('Время отрисовки 96%', max_length=100, blank=True)
    p97 = models.CharField('Время отрисовки 97%', max_length=100, blank=True)
    p98 = models.CharField('Время отрисовки 98%', max_length=100, blank=True)
    p99 = models.CharField('Время отрисовки 99%', max_length=100, blank=True)
    p995 = models.CharField('Время отрисовки 99.5%', max_length=100, blank=True)
    p999 = models.CharField('Время отрисовки 99.9%', max_length=100, blank=True)
    p100 = models.CharField('Время отрисовки 100%', max_length=100, blank=True)
    t10 = models.CharField('Отрисовано за 10 мин., %', max_length=100, blank=True)
    t20 = models.CharField('Отрисовано за 20 мин., %', max_length=100, blank=True)
    t30 = models.CharField('Отрисовано за 30 мин., %', max_length=100, blank=True)
    t40 = models.CharField('Отрисовано за 40 мин., %', max_length=100, blank=True)
    t50 = models.CharField('Отрисовано за 50 мин., %', max_length=100, blank=True)
    t60 = models.CharField('Отрисовано за 60 мин., %', max_length=100, blank=True)
    t70 = models.CharField('Отрисовано за 70 мин., %', max_length=100, blank=True)
    t80 = models.CharField('Отрисовано за 80 мин., %', max_length=100, blank=True)
    t90 = models.CharField('Отрисовано за 90 мин., %', max_length=100, blank=True)
    t100 = models.CharField('Отрисовано за 100 мин., %', max_length=100, blank=True)
    t110 = models.CharField('Отрисовано за 110 мин., %', max_length=100, blank=True)
    t120 = models.CharField('Отрисовано за 120 мин., %', max_length=100, blank=True)
    t130 = models.CharField('Отрисовано за 130 мин., %', max_length=100, blank=True)
    t140 = models.CharField('Отрисовано за 140 мин., %', max_length=100, blank=True)
    t150 = models.CharField('Отрисовано за 150 мин., %', max_length=100, blank=True)
    final_percent = models.FloatField('Процент отрисовки', blank=True, null=True)
    elapsed_time = models.CharField('Время отрисовки', max_length=100, blank=True, null=True)
    max_inactive_time = models.IntegerField('Предельное время бездействия', default=30, blank=True, null=True)
    success_percent = models.FloatField('Cчитать отрисовку успешной при, %', default=100, blank=True, null=True)
    task_id = models.CharField('Celery task ID', max_length=200, blank=True, null=True)
    draw_imgs_type = models.CharField('Тип отрисовки ценников', max_length=20, blank=True, null=True)
    config = models.OneToOneField('Configuration',
                                  on_delete=models.CASCADE, verbose_name='Конфигурация',
                                  null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Отчет об отрисовке ценников"
        verbose_name_plural = "Отрисовки ценников ОТЧЕТЫ"

    def __str__(self):
        return f'Отрисовка ценников #{self.pk}'


class DrawImgsStat(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True, blank=True)
    draw_imgs_report = models.ForeignKey('DrawImgsReport',
                                         on_delete=models.CASCADE, verbose_name='Отчет отрисовки ценников', null=True)
    online_esl = models.IntegerField('Ценников онлайн', blank=True, null=True)
    images_succeeded = models.IntegerField('Отрисованных ценников', blank=True, null=True)
    percent_step = models.IntegerField('Шаг процента отрисовки', blank=True, null=True)
    drawed_percent = models.FloatField('Процент отрисовки (%)', blank=True, null=True)
    elapsed_time = models.CharField('Затраченное время', max_length=50)
    date_time = models.DateTimeField('Дата и время записи',
                                     default=timezone.localtime, blank=True, null=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Отрисовка ценника"
        verbose_name_plural = "Отрисовки ценников"

    def __str__(self):
        return f"Отрисовка ценников #{self.pk} " \
            f"отчета #{self.draw_imgs_report.pk if self.draw_imgs_report.pk else ''}"
