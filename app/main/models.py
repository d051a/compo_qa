from django.db import models


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
    date_time = models.DateTimeField('Дата и время', auto_now_add=True, blank=True, null=True)
    voltage_current = models.FloatField('Текущий вольтаж', blank=True, null=True)
    voltage_average = models.FloatField('Средний вольтаж', blank=True, null=True)

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
    date_time_update = models.DateTimeField('Время обновления данных', auto_now=True)
    config = models.TextField('Текущий конфиг хаоса', blank=True, null=True)
    monitoring_config_params = models.TextField('Отслеживаемые поля конфига', blank=True, null=True)
    compired_config = models.TextField('Результат сравнения конфигов', blank=True, null=True)
    compired_config_date = models.DateTimeField('Дата и время сравнения конфигов', blank=True, null=True)
    compired_config_errs = models.IntegerField('Расхождений в сравниваемых параметрах конфигов',
                                               default=0, blank=True, null=True)
    compired_config_warns = models.IntegerField('Расхождений в параметрах конфигов', default=0, blank=True, null=True)
    multimeter_ip = models.GenericIPAddressField('IP-адрес мультиметра',
                                                 protocol='IPv4', unpack_ipv4=False, blank=True, null=True)

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
    date_time = models.DateTimeField('Дата и время записи', auto_now_add=True, blank=True, null=True)


    class Meta:
        ordering = ["-pk"]
        verbose_name = "Сборка сети"
        verbose_name_plural = "Сборки сети"

    def __str__(self):
        return f'Сборка сети #{self.pk} отчета #{self.net_compile_report}'


class NetCompileReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True, blank=True)
    metric_report = models.ForeignKey('MetricReport',
                                      on_delete=models.CASCADE,
                                      verbose_name='Отчет сбора метрик',
                                      null=True,
                                      blank=True)
    create_date_time = models.DateTimeField('Дата и время создания отчета', auto_now_add=True, blank=True, null=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    net_compile_limit_mins = models.IntegerField('Предельное время сборки сети(мин)',
                                                 default=120, blank=True, null=True)
    net_compile_amount = models.IntegerField('Количество сборок сети', default=1, blank=True, null=True)
    date_time_finish = models.DateTimeField('Дата и время завершения', null=True, blank=True)
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
    p100 = models.CharField('Время сборки 100%', max_length=100, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Отчет сборки сети"
        verbose_name_plural = "Сборки сети ОТЧЕТЫ"

    def __str__(self):
        return f'Отчет сборки сети #{self.pk}'


class MetricReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True)
    create_date_time = models.DateTimeField('Дата и время создания отчета', auto_now_add=True, blank=True, null=True)
    net_compile_limit_mins = models.IntegerField('Предельное время сборки сети(мин)',
                                                 default=120, blank=True, null=True)
    draw_imgs_limit_mins = models.IntegerField('Предельное время отрисовки ценников (мин)',
                                               default=300, blank=True, null=True)
    net_compile_amount = models.IntegerField('Количество сборок сети', default=1, blank=True, null=True)
    draw_imgs_amount = models.IntegerField('Количество отрисовок', default=1, blank=True, null=True)
    fact_total_esl = models.IntegerField('Фактическое количество ESL онлайн', null=True, blank=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    date_time_finish = models.DateTimeField('Дата и время завершения', null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Метрика Хаоса"
        verbose_name_plural = "Метрики Хаоса"

    def __str__(self):
        return f'Метрика хаоса #{self.pk}'


class DrawImgsReport(models.Model):
    chaos = models.ForeignKey('Chaos', on_delete=models.CASCADE, verbose_name='Хаос', null=True, blank=True)
    metric_report = models.ForeignKey('MetricReport',
                                      on_delete=models.CASCADE,
                                      verbose_name='Отчет сбора метрик',
                                      null=True,
                                      blank=True)
    create_date_time = models.DateTimeField('Дата и время создания отчета', auto_now_add=True, blank=True, null=True)
    date_time_finish = models.DateTimeField('Дата и время окончания отчета', blank=True, null=True)
    draw_imgs_limit_mins = models.IntegerField('Предельное время отрисовки ценников (мин)',
                                               default=300, blank=True, null=True)
    draw_imgs_amount = models.IntegerField('Количнство отрисовок ценников', default=1, blank=True, null=True)
    status = models.CharField('Статус', max_length=200, blank=True)
    fact_total_esl = models.IntegerField('Фактическое количество ESL онлайн', null=True, blank=True)
    drawed_esl = models.IntegerField('Отрисовано ценников', null=True, blank=True)
    not_drawed_esl = models.IntegerField('Неотрисовано ценников', null=True, blank=True)
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
    p100 = models.CharField('Время отрисовки 100%', max_length=100, blank=True)

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
    date_time = models.DateTimeField('Дата и время записи', auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Отрисовка ценника"
        verbose_name_plural = "Отрисовки ценников"

    def __str__(self):
        return f"Отрисовка ценников #{self.pk} отчета #{self.draw_imgs_report.pk if self.draw_imgs_report.pk else ''}"