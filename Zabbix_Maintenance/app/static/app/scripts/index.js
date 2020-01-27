$(function () {

    // get cookie by name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    // check needed cookie csrf or not
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // options of notify check bootstrap-notify.js
    function Notify_options(status) {
        let options = {
            allow_dismiss: true,
            newest_on_top: true,
            placement: {
                from: "bottom",
                align: "right"
            },
            type: '',
            delay: 5000,
            animate: {
                enter: 'animated zoomInUp',
                exit: 'animated zoomOutDown'
            },
            template: '<div data-notify="container" class="col-xs-11 col-sm-3 alert alert-{0}" role="alert">' +
                '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
                '<span data-notify="title">{1}</span>' +
                '<span data-notify="message">{2}</span>' +
                '</div>'
        }
        if (status == 'error' || status == 'error-minimalist') {
            options.type = 'error-minimalist';
        }
        if (status == 'success' || status == 'success-minimalist') {
            options.type = 'success-minimalist';
        }
        return options
    }


    function table_add_row(table, cells) {
        let tbody = table.children('tbody').eq(0);
        let number = 1;
        if (parseInt(tbody.find('th').last().text())) {                  // находим номер последней строки и добавлем единицу
            number = 1 + parseInt(tbody.find('th').last().text());
        }
        let tr = $('<tr></tr>');
        let th = $('<th></th>');
        th.text(number);                                                // устанавливаем текст с номером строки
        th.attr('scope', 'row');                                        // добавляем бустрап аттрибут
        let td1 = $('<td></td>');
        td1.text(cells.status);
        let td2 = $('<td></td>');
        td2.text(cells.hosts);
        // добавляем строку в DOM
        th.appendTo(tr);
        td1.appendTo(tr);
        td2.appendTo(tr);
        tr.appendTo(tbody);
    }


    $('#btn_check_crq').unbind('click');
    $('#btn_check_crq').bind('click', check_crq);
    $('#btn_mm_create').unbind('click');
    $('#btn_mm_create').bind('click', btn_handler_create_mm);


    function check_crq() {
        let that = $(this)
        let input_crq = $('#input_crq')
        let crq = $('#input_crq').val()
        forms = $('.needs-validation')
        forms.addClass('was-validated')
        csrf = forms.children('input[name="csrfmiddlewaretoken"]').val()
        if (crq != '') {
            let span = $('<span>', {
                'class': 'spinner-border spinner-border-sm',
                'role': 'status',
                'aria-hidden': 'true'
            });
            that.text('Загрузка...')    // изменяем текст кнопки с проверить на загрузку
            span.appendTo(that);    // Добавляем спинер
            $.ajax({
                url: 'get_crq_time/',
                method: 'POST',
                dataType: 'json',
                data: {
                    'crq': crq,
                    'csrfmiddlewaretoken': csrf
                },
                success: function (data) {
                    input_crq.removeClass('is-invalid')
                    $('#invalid_crq').text('Введите номер CRQ')
                    if (data.error.code != 0) {
                        forms.removeClass('was-validated')
                        $('#invalid_crq').text(data.error.message)
                        input_crq.addClass('is-invalid')
                    }
                    else {
                        let start = new Date(data.content.start_time)
                        let end = new Date(data.content.end_time)
                        start = start.toLocaleString()
                        end = end.toLocaleString()
                        $('#input_start').val(start)
                        $('#input_end').val(end)
                    }
                },
                error: function () {
                    forms.removeClass('was-validated')
                    $('#invalid_crq').text('Что-то не так с CRQ')
                    input_crq.addClass('is-invalid')
                },
                complete: function () {
                    that.children().remove()    // Убираем спиннер
                    that.text('Проверить')      // Возвращаем текст кнопки на проверить
                }
            })
        }
    }


    function btn_handler_create_mm() {
        $('#ModalCreateMM').modal('hide');
        let form = $('#ModalCreateMM').find('form').first();
        let hg_with_h = []          // list hostgroups with hosts in that hostgrousps
        let stands = [];            // list stands with name and id [ {'id': id, 'name': name}, ...} ]
        let select_list = form.find('select');
        let select=null;
        let select2=null;
        if (select_list.length == 1) {
            select2 = form.find('select').eq(0); // first select in form
        }
        if (select_list.length >= 2) {
            select = form.find('select').eq(0); // first select in form
            select2 = form.find('select').eq(1); // second select in form
        }
        if (select != null) {
            select.find('optgroup').each(function () {
                let hosts = [];
                $(this).find('option:selected').each(function () {
                    hosts.push({
                        'id': $(this).attr('value'), 'name': $(this).text(), 'zabbix': $(this).attr('data-subtext') });
                });
                if (hosts.length != 0) {
                    let id = $(this).attr('value');
                    let name = $(this).attr('label');
                    let zabbix = $(this).attr('data-subtext');
                    hg_with_h.push({ 'id': id, 'name': name, 'zabbix': zabbix, 'hosts': hosts });
                }
            });
        }
        if (hg_with_h.length == 0) {
            select2.find('option:selected').each(function () {
                stands.push({ 'id': $(this).attr('value'), 'name': $(this).text() });
            });
            if (stands.length == 0) {
                $.notify({
                    title: 'Создание режима обслуживания',
                    message: 'Выберите хосты или площадки'
                }, Notify_options('error'));
                return
            }
        }

        // находим дату и время регулярками на основе которых будем создавать дату
        let re = /([0-9]{2}).([0-9]{2}).([0-9]{4})/;
        let start_date = $('#input_start').val();
        let end_date = $('#input_end').val();
        start_date = start_date.match(re);
        end_date = end_date.match(re);
        let re_time = /([0-9]{2}):([0-9]{2}):([0-9]{2})/;
        let start_time = $('#input_start').val();
        let end_time = $('#input_end').val();
        start_time = start_time.match(re_time);
        end_time = end_time.match(re_time);
        // создаем корректный объект Date и парсим его как Json строку
        // При создании Date из 2 аргумента вычитаем еденицу, т.к. это месяц а месяцы с 0 до 11
        let start = new Date(parseInt(start_date[3]), parseInt(start_date[2])-1, parseInt(start_date[1]), parseInt(start_time[1]), parseInt(start_time[2]), parseInt(start_time[3]));
        start = start.toJSON();
        let end = new Date(parseInt(end_date[3]), parseInt(end_date[2])-1, parseInt(end_date[1]), parseInt(end_time[1]), parseInt(end_time[2]), parseInt(end_time[3]));
        end = end.toJSON();

        $.ajax({
            url: 'create_mm/',
            method: 'POST',
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            },
            contentType: "application/json",
            dataType: 'json',
            data: JSON.stringify({
                'crq': $('#input_crq').val(),
                'start': start,
                'end': end,
                'hg_with_h': hg_with_h,
                'stands': stands,
            }),
            async: true,
            success: function (data) {
                if (data.error.code == 0) {
                    $.notify({
                        title: 'Создание режима обслуживания',
                        message: 'Режим обслуживания успешно создан'
                    }, Notify_options('success'));
                    table_add_row($('#table_mm'), { 'status': data.content.status, 'hosts': data.content.hosts });
                    $('#ModalCreateMM').find('form').get(0).reset();
                    form.find('select').eq(0).selectpicker('deselectAll');
                    form.find('select').eq(1).selectpicker('deselectAll');
                }
                else {
                    let msg = 'Ошибка сервера при создании режима обслуживания';
                    if (data.error.message) {
                        msg = data.error.message;
                    }
                    $.notify({
                        title: 'Создание режима обслуживания',
                        message: msg
                    }, Notify_options('error'));
                }
            },
            error: function () {
                $.notify({
                    title: 'Создание режима обслуживания',
                    message: 'Ошибка при создании режима обслуживания'
                }, Notify_options('error'));
            },
            complete: function () {
                //TODO
                //refresh page or insert/delete row(s) in table
            }
        })
    }
});