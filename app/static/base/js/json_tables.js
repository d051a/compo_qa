

$(document).ready(function() {
    var metric_reports_list_url = $("#metric_reports_list_url").attr("data-url");
    var report_all_stats_list_url = $("#report_all_stats_list_url").attr("data-url");
    var report_net_compiles_list_url = $("#report_net_compiles_list_url").attr("data-url");
    var report_drawed_imgs_list_url = $("#report_drawed_imgs_list_url").attr("data-url");
    var report_drawed_imgs_stats_url = $("#report_drawed_imgs_stats_url").attr("data-url");
    var net_compile_stats_url = $("#net_compile_stats_url").attr("data-url");
    var metric_report_pk = $("#metric_report_pk").attr("data-url");
    var chaos_pk = $("#chaos_pk").attr("data-url");


     $('#static_datatable').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Aucun &eacute;l&eacute;ment &agrave; afficher",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

        $('#all_metrics_list').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "ajax": {"url": metric_reports_list_url,
        "data":  {"chaos_pk": chaos_pk, "report_pk": metric_report_pk}},
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Aucun &eacute;l&eacute;ment &agrave; afficher",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

                 $('#report_drawed_list').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "lengthChange": false,
        "ajax": {"url": report_drawed_imgs_list_url,
        "data":  {"chaos_pk": chaos_pk, "report_pk": metric_report_pk}},
                "lengthMenu": [[5, 25, 50, -1], [10, 25, 50, "All"]],
                dom: 'Bfrtip',
                buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
                language: {
                  processing:     "Traitement en cours...",
                  search:         "Поиск",
                  lengthMenu:     "Показать _MENU_ элементов",
                  info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
                  infoEmpty:      "Показано 0 из 0 из 0 элементов",
                  infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
                  infoPostFix:    "",
                  loadingRecords: "Chargement en cours...",
                  zeroRecords:    "Нет данных",
                  emptyTable:     "Нет данных",
                  paginate: {
                        first:      "Первый",
                        previous:   "Предыдущий",
                        next:       "Следующий",
                        last:       "Последний"
            },},
                searching: true,
    });

         $('#report_all_stats_list').dataTable({
         "scrollY": "550px",
         "sScrollX": "100%",
         "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "ajax": {"url": report_all_stats_list_url,
        "data":  {"chaos_pk": chaos_pk, "report_pk": metric_report_pk}},
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Нет данных",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

        $('#drawed_stats_list').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "ajax": {"url": report_drawed_imgs_stats_url,
        "data":  {"report_pk": metric_report_pk}},
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Нет данных",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

        $('#net_compile_stats').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "ajax": {"url": net_compile_stats_url,
        "data":  {"report_pk": metric_report_pk}},
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Нет данных",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

                $('#report_net_compiles_list').dataTable({
        "scrollY":        "550px",
        "scrollCollapse": true,
        "paging":         true,
        "ordering":       false,
        "pagingType":     "numbers",
        "processing":     true,
        "serverSide":     true,
        "ajax": {"url": report_net_compiles_list_url,
        "data":  {"chaos_pk": chaos_pk, "report_pk": metric_report_pk}},
        "lengthMenu": [[5, 25, 50, -1], [10, 25, 50, "All"]],
        dom: 'Bfrtip',
        buttons: ['pageLength', 'copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
          processing:     "Traitement en cours...",
          search:         "Поиск",
          lengthMenu:     "Показать _MENU_ элементов",
          info:           "Показано _START_ из _END_ из _TOTAL_ элементов",
          infoEmpty:      "Показано 0 из 0 из 0 элементов",
          infoFiltered:   "(Отфильтровано из _MAX_ позиций)",
          infoPostFix:    "",
          loadingRecords: "Chargement en cours...",
          zeroRecords:    "Нет данных",
          emptyTable:     "Нет данных",
          paginate: {
                first:      "Первый",
                previous:   "Предыдущий",
                next:       "Следующий",
                last:       "Последний"
            },},
                searching: true,
    });

});