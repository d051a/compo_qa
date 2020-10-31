net_compile_short_report_draw_fields = ['create_date_time', 'status', 'date_time_finish', 'name', 'ip',
                                        'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100']

draw_imgs_stats_short_report_draw_fields = ['create_date_time', 'status', 'date_time_finish', 'name', 'ip',
                                            'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100']

net_compile_reports_draw_fields = ['create_date_time', 'status',
                                   'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100',
                                   'fact_total_esl', 'date_time_finish',
                                   ]
draw_imgs_reports_draw_fields = ['create_date_time', 'status',
                                 'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100', 'fact_total_esl',
                                 'drawed_esl', 'not_drawed_esl', 'date_time_finish'
                                 ]
draw_imgs_stat_fields = ['percent_step', 'elapsed_time', 'images_succeeded']
net_compile_stat_fields = ['compilation_percent', 'online_esl', 'elapsed_time']
metrics_report_common_statistic_draw_fields = ['date_time',
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
                                               'network_mode_percent',
                                               'voltage_average',
                                               'voltage_current',
                                               'voltage_max',
                                               'bat_reserved1',
                                               'bat_reserved2',
                                               'bat_reserved3',
                                               'bat_reserved4',
                                               ]

net_compile_fields_common_report = ['create_date_time', 'elapsed_time', 'final_percent', 't60', 'fact_total_esl',
                                    'status',
                                    ]
draw_imgs_fields_common_report = ['p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p995', 'p999', 'p100',
                                  'not_drawed_esl',
                                  ]
net_compile_fields_common_extended_report = ['create_date_time', 'elapsed_time', 'final_percent', 'status',
                                             'p10', 'p20', 'p30', 'p40', 'p50', 'p60', 'p75', 'p90', 'p95', 'p96',
                                             'p97', 'p98', 'p99', 'p995', 'p999', 'p100',
                                             't10', 't20', 't30', 't40', 't50', 't60', 't70', 't80', 't90', 't100',
                                             't110', 't120', 't130', 't140', 't150',
                                             'fact_total_esl',
                                             'success_percent',
                                             ]
draw_imgs_fields_common_extended_report = ['create_date_time',
                                           'date_time_finish',
                                           'draw_imgs_limit_mins',
                                           'p10', 'p20', 'p30', 'p40', 'p50', 'p60', 'p75', 'p90', 'p95', 'p96',
                                           'p97', 'p98', 'p99', 'p995', 'p999', 'p100',
                                           't10', 't20', 't30', 't40', 't50', 't60', 't70', 't80', 't90', 't100',
                                           't110', 't120', 't130', 't140', 't150',
                                           'drawed_esl',
                                           'not_drawed_esl',
                                           'final_percent',
                                           'draw_imgs_type',
                                           'status',
                                           ]


chaos_configuration_fields = ['shields_num',
                              'hardware_config',
                              'total_esl',
                              'dd_nums',
                              'dd_configuration',
                              'dd_dongles_num',
                              'version_sum',
                              'version_chaos',
                              'chaos_configuration',
                              'tree_floor_num',
                              'version_driver',
                              'version_esl_firmware',
                              'version_esl_hw',
                              'version_dongles_hw',
                              ]
