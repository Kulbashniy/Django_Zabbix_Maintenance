$(function () {
    // get cookie
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

    // ----------------------- TABLE --------------------------- //
    class Table {

        constructor(tbody) {
            this.selected_rows = [];  // selected table rows (stands name)
            this.control_elems = [];  // control elements (jqery btn elements)
            // @param tbody - jquery element
            // init the table logic
            self = this;
            let tr_list = tbody.children('tr');
            tr_list.off('click');
            tr_list.on('click', this.tr_click);
            this.control_elems.push($('#btn_create_stand'));
            this.control_elems.push($('#btn_change_stand'));
            this.control_elems.push($('#btn_delete_stand'));
            this.change_btn_state();
        }

        tr_click(event) {

            let th = $(this).children('th').first();
            let checkbox = th.children(':checkbox').first();
            if (checkbox.is(':checked')) {
                self.deselect_row($(this));
            }
            else {
                self.select_row($(this));
            }
        }

        select_row(tr_elem) {
            let checkbox = tr_elem.find(':checkbox').first();
            checkbox.prop('checked', true);
            let row = tr_elem.children('td').first().text();
            if ($.inArray(row, self.selected_rows) == -1) {
                self.selected_rows.push(row);
            }
            else {
                return
            }
            self.change_btn_state();    // Изменяем состояние кнопок
        }

        deselect_row(tr_elem) {
            let checkbox = tr_elem.find(':checkbox').first();
            checkbox.prop('checked', false);
            let row = tr_elem.children('td').first().text();
            if ($.inArray(row, self.selected_rows) != -1) {
                self.selected_rows.splice(self.selected_rows.indexOf(row), 1);    // Удаляем 
            }
            else {
                return
            }
            self.change_btn_state();    // Изменяем состояние кнопок
        }

        add_row(dict_cells) {
            // @param - dict_cells= dict of name:value of cells {'name': 'M9', 'hosts': 'host1, host2'}
            if (dict_cells.name != '' && dict_cells.hosts != '') {
                let tbody = $('#stands_tbody');
                let id = tbody.find('tr').last().find(':checkbox').first().attr('id');
                let row_number = 1;
                if (id) {
                    row_number = 1 + parseInt(id.substr(4));
                }
                id = 'box-' + row_number;
                let tr = $('<tr></tr>');
                let th1 = $('<th style="vertical-align: middle"></th>');
                let input = $('<input type="checkbox" id="' + id + '">');
                let label = $('<label for="' + id + '"></label>')
                input.appendTo(th1);
                label.appendTo(th1);
                th1.appendTo(tr);
                let th2 = $('<th scope="row">'+row_number+'</th>');
                th2.appendTo(tr);
                let td1 = $('<td>' + dict_cells.name + '</td>');
                td1.appendTo(tr);
                let td2 = $('<td>' + dict_cells.hosts + '</td>')
                td2.appendTo(tr);
                tr.off('click');
                tr.on('click', self.tr_click)
                tr.appendTo(tbody);
            }
            else {
                console.log('Not enough parameters to create row view');
            }
        }

        change_row(target_row ,dict_cells) {
            // @param - dict_cells = dict of name:value of cells {'name': 'M9', 'hosts': 'host1, host2'}
            // @param - target_row = stand_name (like old_stand name, and new_stand name in dict cells)
            if (target_row!='' && dict_cells.name != '' && dict_cells.hosts != '') {
                let tbody = $('#stands_tbody');
                tbody.find('tr>td:nth-of-type(1)').each(function (ind, elem) {
                    if (target_row == $(this).text()) {
                        let tr = $(this).parent();
                        table.deselect_row(tr)
                        $(this).text(dict_cells.name);
                        tr.find('td').eq(1).text(dict_cells.hosts);                     // Второй td элемент в строке
                    }
                })
            }
            else {
                console.log('Not enough parameters to change row view');
            }
            self.change_btn_state();    // Изменяем состояние кнопок
        }

        delete_rows(stands_list) {
            // if you added the column before first td use another selector to remove rows
            let tbody = $('#stands_tbody');
            stands_list.forEach(function (stand) {
                tbody.find('tr>td:nth-of-type(1)').each(function (ind, elem) {
                    if (stand == $(this).text()) {
                        $(this).parent().remove();
                    }
                })
                if ($.inArray(stand, self.selected_rows) != -1) {
                    self.selected_rows.splice(self.selected_rows.indexOf(stand), 1);    // Удаляем 
                }
                else {
                    return
                }
            })
            tbody.find('tr').each(function (row_number) {
                $(this).children('th').each(function (index) {
                    if (index == 0) {
                        $(this).children(':checkbox').first().attr('id', 'box-' + (row_number + 1));
                        $(this).children('label').first().attr('for', 'box-' + (row_number + 1));
                    }
                    if (index == 1) {
                        $(this).text((row_number + 1));
                    }
                })
            });
            self.change_btn_state();    // Изменяем состояние кнопок
        }

        change_btn_state() {
            // change control_elems(buttons) states disabled to true/false
            if (self.selected_rows.length == 0) {
                self.control_elems.forEach(function (control_elem) {
                    if (control_elem.attr("id") == 'btn_change_stand') {
                        control_elem.prop('disabled', true);
                    }
                    if (control_elem.attr("id") == 'btn_delete_stand') {
                        control_elem.prop('disabled', true);
                    }
                });
            }
            if (self.selected_rows.length == 1) {
                self.control_elems.forEach(function (control_elem) {
                    if (control_elem.attr("id") == 'btn_change_stand') {
                        control_elem.prop('disabled', false);
                    }
                    if (control_elem.attr("id") == 'btn_delete_stand') {
                        control_elem.prop('disabled', false);
                    }
                });
            }
            if (self.selected_rows.length > 1) {
                self.control_elems.forEach(function (control_elem) {
                    if (control_elem.attr("id") == 'btn_change_stand') {
                        control_elem.prop('disabled', true);
                    }
                    if (control_elem.attr("id") == 'btn_delete_stand') {
                        control_elem.prop('disabled', false);
                    }
            });
            }   
        }
    }


    // --------------------- MODAL --------------------------- //
    class Modal {

        constructor (div_modal) {
            // @param - div_modal jquery elem
            // @param - table class Table that associate with modal
            this.modal = div_modal;
            this.set_handler(this.modal.find('button[control-button="true"]'), this.get_correct_handler('click'), 'click');
            this.set_handler(this.modal, this.get_correct_handler('show.bs.modal'), 'show.bs.modal');
        }

        get_correct_handler(event) {
            // @param - event = type of event (such as 'click'), handler which we want get
            let id = this.modal.attr('id');
            if (id == 'ModalStandCreate') {
                if (event == 'click') {
                    return this.handler_create
                }
            }
            if (id == 'ModalStandChange') {
                if (event == 'click') {
                    return this.handler_change
                }
                if (event == 'show.bs.modal') {
                    return this.handler_modal_change_show
                }
            }
            if (id == 'ModalStandDelete') {
                if (event == 'click') {
                    return this.handler_delete
                }
                if (event == 'show.bs.modal') {
                    return this.handler_modal_delete_show
                }
            }
        }

        set_handler(elem, handler, handler_type) {
            // @param - elem = the element on which the handler associate
            // @param - handler = handler function
            // @param - handler_type = type of handler such as 'click' and e.t.c
            elem.off(handler_type);
            elem.on(handler_type, handler);
        }

        handler_create() {
            // handler on button create in modal create stand
            $('#ModalStandCreate').modal('hide');
            let form = $('#ModalStandCreate').find('form').first();
            let hg_with_h = [] // list hostgroups with hosts in that hostgrousps
            let select = form.find('select').eq(0); // first select in form
            select.find('optgroup').each(function () {
                let hosts = [];
                $(this).find('option:selected').each(function () {
                    hosts.push({ 'id': $(this).attr('value'), 'name': $(this).text(), 'zabbix': $(this).attr('data-subtext') });
                });
                if (hosts.length != 0) {
                    let id = $(this).attr('value');
                    let name = $(this).attr('label');
                    let zabbix = $(this).attr('data-subtext');
                    hg_with_h.push({ 'id': id, 'name': name, 'zabbix': zabbix, 'hosts': hosts });
                }
            });
            $.ajax({
                url: 'create_stand/',
                method: 'POST',
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                },
                contentType: "application/json",
                dataType: 'json',
                data: JSON.stringify({
                    'name': $('#input_name_modal_create').val(),
                    'hg_with_h': hg_with_h,
                }),
                async: true,
                success: function (data) {
                    if (data.error.code == 0) {
                        $.notify({
                            title: 'Создание площадки',
                            message: 'Площадка была успешна создана'
                        }, Notify_options('success'));
                        table.add_row({ 'name': data.content.name, 'hosts': data.content.hosts });
                        $('#ModalStandCreate').find('form').get(0).reset();
                        form.find('select').eq(0).selectpicker('deselectAll');
                    }
                    else {
                        let msg = 'Ошибка сервера при создании площадки';
                        if (data.error.message) {
                            msg = data.error.message;
                        }
                        $.notify({
                            title: 'Создание площадки',
                            message: msg
                        }, Notify_options('error'));
                    }
                },
                error: function () {
                    $.notify({
                        title: 'Создание площадки',
                        message: 'Ошибка при создании площадки'
                    }, Notify_options('error'));
                },
                complete: function () {
                    //TODO
                    //refresh page or insert/delete row(s) in table
                }
            })
        }

        handler_change() {
            $('#ModalStandChange').modal('hide');
            let form = $('#ModalStandChange').find('form').first();
            let hg_with_h = [] // list hostgroups with hosts in that hostgrousps
            let select = form.find('select').eq(0); // first select in form
            select.find('optgroup').each(function () {
                let hosts = [];
                $(this).find('option:selected').each(function () {
                    hosts.push({ 'id': $(this).attr('value'), 'name': $(this).text(), 'zabbix': $(this).attr('data-subtext') });
                });
                if (hosts.length != 0) {
                    let id = $(this).attr('value');
                    let name = $(this).attr('label');
                    let zabbix = $(this).attr('data-subtext');
                    hg_with_h.push({ 'id': id, 'name': name, 'zabbix': zabbix, 'hosts': hosts });
                }
            });
            let new_name = $('#input_name_modal_change').val();
            $.ajax({
                url: 'change_stand/',
                method: 'POST',
                beforeSend: function (xhr, settings) {      // set cookie header in ajax request
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                },
                contentType: "application/json",
                dataType: 'json',
                data: JSON.stringify({
                    'old_name': table.selected_rows[0],
                    'new_name': new_name,
                    'hg_with_h': hg_with_h
                }),
                async: true,
                success: function (data) {
                    if (data.error.code == 0) {
                        table.change_row(data.content.old_name, { 'name': data.content.new_name, 'hosts': data.content.hosts });
                        let msg = data.error.message;
                        $.notify({
                            title: 'Изменение площадки',
                            message: msg,
                        }, Notify_options('success'));
                    }
                    else {
                        let msg = 'Ошибка сервера при изменении площадки';
                        if (data.error.message) {
                            msg = data.error.message;
                        }
                        $.notify({
                            title: 'Изменение площадки',
                            message: msg
                        }, Notify_options('error'));
                    }
                },
                error: function () {
                    $.notify({
                        title: 'Изменение площадки',
                        message: 'Ошибка при изменении площадки'
                    }, Notify_options('error'));
                },
                complete: function () {
                    //TODO
                    //refresh page or insert/delete row(s) in table
                }
            })

        }

        handler_delete() {
            // handler on button delete in modal delete stand
            $('#ModalStandDelete').modal('hide');
            let form = $('#ModalStandDelete').find('form').first();
            let csrf = form.children('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: 'delete_stand/',
                method: 'POST',
                dataType: 'json',
                data: {
                    'names': table.selected_rows,
                    'csrfmiddlewaretoken': csrf
                },
                async: true,
                success: function (data) {
                    if (data.error.code == 0) {
                        table.delete_rows(data.content.names);
                        let msg = data.error.message;
                        $.notify({
                            title: 'Удаление площадки',
                            message: msg,
                        }, Notify_options('success'));
                    }
                    else {
                        let msg = 'Ошибка сервера при удалении площадки';
                        if (data.error.message) {
                            msg = data.error.message;
                        }
                        $.notify({
                            title: 'Удаление площадки',
                            message: msg
                        }, Notify_options('error'));
                    }
                },
                error: function () {
                    $.notify({
                        title: 'Удаление площадки',
                        message: 'Ошибка при удалении площадки'
                    }, Notify_options('error'));
                },
                complete: function () {
                    //TODO
                    //refresh page or insert/delete row(s) in table
                }
            })
        }


        handler_modal_change_show() {
            // handler when show modal to change stand
            let form = $(this).find('form').first();
            $('#input_name_modal_change').val(table.selected_rows[0]);
            let select = form.find('select').eq(0)
            select.selectpicker('deselectAll');  // deselect all selected options
            // select hosts which contain current stand
        }


        handler_modal_delete_show() {
            // handler when show modal to delete stand
            let form = $(this).find('form').first();
            let ul = $("<ul id='modal_delete_stands_list' class='list-group list-group-flush'></ul>");
            table.selected_rows.forEach(function (row) {    // create li with names of stands
                let li = $("<li class='list-group-item'>" + row + "</li>");
                li.appendTo(ul);
            })
            if ($('#modal_delete_stands_list').length) {
                ul.replaceAll($('#modal_delete_stands_list'));
            }
            else {
                ul.appendTo(form);  // append ul list with stands to form
            }
        }


    }


    let table = new Table($('#stands_tbody'));
    let modal_create = new Modal($('#ModalStandCreate'), table);
    let modal_change = new Modal($('#ModalStandChange'), table);
    let modal_del = new Modal($('#ModalStandDelete'), table);

});