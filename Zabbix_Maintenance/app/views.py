"""
Definition of views.
"""

from datetime import datetime, timezone
import pytz
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required   # to use login_required decorator
from django.contrib.auth import views                       # to use custom auth views
from django.core.cache import cache                         # import lov-level cache api to cache data (like request to zabbix)
from app.static.app.python_scripts.skuf import Skuf
from app.static.app.python_scripts.zabbix import Zabbix
from app.models import *                                    # to use models in view


"""
Template JSON response
{
    'error': {'code': value, 'message': message_text},
    'content': {'example': example_value, ....}
}
"""

@login_required
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    hg_with_h = cache.get('hg_with_h')                          # read hosts with hostgroups from cache
    if hg_with_h is None:
        hg_with_h = Zabbix.get_hg_with_h()                      # return None if fail else list
        cache.set('hg_with_h', hg_with_h, 86400)                # set 1-day cache of request to Zabbix (get hosts with hostgroups)
    return render(
        request,
        'app/index.html',
        {
            'title':'Главная',
            'year':datetime.now().year,
            'mms': request.user.person.get_mm(),                # post all Person Maintenance modes in view
            'hg_with_h': hg_with_h,                             # post list [ { 'id': '@host_group_id', 'name': '@host_group_name', 'zabbix': '@zabbixurl', 'hosts': [{'id': '@host_id', 'name': '@host_name', 'zabbix': '@zabbixurl'}, ...] }, ...]
            'stands': Stand.objects.all()                       # post all stands in view
        }
    )


@login_required
def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

@login_required
def get_crq_time(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        import json                                          
        crq = request.POST.dict()['crq']
        response = Skuf.get_crq_time(crq)                               # skuf class (static python_script)
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return

@login_required
def stands(request):
    assert isinstance(request, HttpRequest)
    hg_with_h = cache.get('hg_with_h')                          # read hosts with hostgroups from cache
    if hg_with_h is None:
        hg_with_h = Zabbix.get_hg_with_h()                      # return None if fail else list
        cache.set('hg_with_h', hg_with_h, 86400)                # set 1-day cache of request to Zabbix (get hosts with hostgroups)
    if request.method == 'POST':                                    # check POST data
        if request.POST.get('key')=='xxxxxxxx':                 # key to access to stands
            request.user.person.set_admin()                         # set admin status to True
    return render(  
        request,
        'app/stands.html',
        {
            'title': 'Площадки',
            'year':datetime.now().year,
            'person': request.user.person,
            'stands': Stand.objects.all(),                          # post all stands in view
            'hg_with_h': hg_with_h                                  # post list [ { 'id': '@host_group_id', 'name': '@host_group_name', 'zabbix': '@zabbixurl', 'hosts': [{'id': '@host_id', 'name': '@host_name', 'zabbix': '@zabbixurl'}, ...] }, ...]
        }
    )

@login_required
def create_mm(request):
    # Create Maintenance Mode and return response
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            crq = data.get('crq')
            start = data.get('start')
            end = data.get('end')
            hg_with_h = data.get('hg_with_h')
            stands = data.get('stands')
            if hg_with_h and stands:
                response = {'error': {'code': 4, 'message': 'Нельзя выбрать и площадки и хосты, выберите либо площадки, либо хосты, режим обслуживания не был создан'}}
            if crq and start and end and (hg_with_h or stands):
                start = start[:start.find('Z')]                 # обрезаем тайм зону она +0 (+3 это МСК)
                start = datetime.fromisoformat(start)           # делаем datetime но tz не указываем
                start = start.replace(tzinfo=pytz.UTC)          # ставим tz=0
                end = end[:end.find('Z')]                       # обрезаем тайм зону она +0 (+3 это МСК)
                end = datetime.fromisoformat(end)               # делаем datetime но tz не указываем
                end = end.replace(tzinfo=pytz.UTC)              # ставим tz=0
                timestamp_start = int(start.timestamp())        # int value - posix timestamp start of MM
                timestamp_end = int(end.timestamp())            # int value - posix timestamp end of MM
                if hg_with_h:                   
                    hostids = list()                            # create list of hostids
                    for hg in hg_with_h:
                        for host in hg['hosts']:
                            hostids.append({'id': host['id'], 'zabbix': host['zabbix']})
                    response = Zabbix.create_mm(description=request.user.username, name=crq, start=timestamp_start, end=timestamp_end, hostids=hostids)
                    if response.get('error').get('code') == 11:
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    elif response.get('error').get('code') == 12:
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    mm_obj = Maintenance_mode.objects.create(person=request.user.person, start_time=start, end_time=end)
                    mm_obj.set_mm_hosts(hg_with_h=hg_with_h)
                else:
                    hostids = list()                                                # create list of hostids
                    for stand in stands:
                        stand_obj = Stand.objects.get(id=stand['id'])               # get list of host ids
                        hostids.extend(stand_obj.get_host_list_zabbix_and_ids())    # extend list by list
                    response = Zabbix.create_mm(description=request.user.username, name=crq, start=timestamp_start, end=timestamp_end, hostids=hostids)
                    if response.get('error').get('code') == 11:
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    elif response.get('error').get('code') == 12:
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    elif response.get('error').get('code') == 13:
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    mm_obj = Maintenance_mode.objects.create(person=request.user.person, start_time=start, end_time=end)
                    mm_obj.set_mm_hosts(stands=stands)
                response = {'error': {'code': 0 , 'message': 'Режим обслуживания успешно создан'}, 'content': {'status': mm_obj.status, 'hosts': mm_obj.get_hosts()}}
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                response = {'error': {'code': 2, 'message': 'Необходимые поля не заполнены, режим обслуживания не был создан'}}
                return HttpResponse(json.dumps(response), content_type='application/json')
            response = {'error': {'code': 0 , 'message': 'Режим обслуживания успешно создан'}, 'content': {'status': mm_obj.status, 'hosts': mm_obj.get_hosts}}
        except:
            response = {'error': {'code': 1, 'message': 'При создании режима обслуживания что-то пошло не так, режим обслуживания не был создан'}}
        finally:
            return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return


@login_required
def create_stand(request):
    # Create Stand and return response
    assert isinstance(request, HttpRequest)
    if request.user.person.is_admin():
        if request.method == 'POST':
            import json
            try:
                data = json.loads(request.body)
                name = data.get('name')
                hg_with_h = data.get('hg_with_h')
                if len(name) == 0 or len(hg_with_h) == 0:
                    response = {'error': {'code': 3, 'message': 'Обязательные поля не были заполнены'}}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                stand = Stand(name=name)
                msg = stand.save(hg_h=hg_with_h)
                if msg:
                    response = {'error': {'code': 3, 'message': msg}}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                response = {'error': {'code': 0, 'message': 'Успешно создано'}, 'content': {'name': name, 'hosts': stand.display_host()}}
            except:
                response = {'error': {'code': 1, 'message': 'При создании площадки что-то пошло не так, площадка не была создана'}}
            finally:
                return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            return
    else:
        return


@login_required
def change_stand(request):
    # Change Stand and return response
    assert isinstance(request, HttpRequest)
    if request.user.person.is_admin():
        if request.method == 'POST':
            import json
            try:
                data = json.loads(request.body)
                old_name = data.get('old_name')
                new_name = data.get('new_name')
                hg_with_h = data.get('hg_with_h')
                if len(hg_with_h) == 0:
                    response = {'error': {'code': 3, 'message': 'Обязательные поля не были заполнены'}}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                stand = Stand.objects.get(name=old_name)
                msg = stand.update(name=new_name, hg_h=hg_with_h) #hg_h - список хостгрупп со списком хостов в этих хостгруппах
                if msg:
                    response = {'error': {'code': 3, 'message': msg}}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                hosts = stand.get_hosts_list()
                response = {'error': {'code': 0, 'message': 'Успешно изменено'}, 'content': {'old_name': old_name, 'new_name': new_name, 'hosts': hosts}}
            except Stand.DoesNotExist:
                response = {'error': {'code': 2, 'message': 'Площадка с таким именем не существует'}}
            except:
                response = {'error': {'code': 1, 'message': 'При изменении площадки что-то пошло не так, площадка не была изменена'}}
            finally:
                return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            return
    else:
        return


@login_required
def delete_stand(request):
    # Delete Stand and return response
    assert isinstance(request, HttpRequest)
    if request.user.person.is_admin():
        if request.method == 'POST':
            import json
            try:
                names = request.POST.getlist('names[]')
                for name in names:
                    stand = Stand.objects.get(name=name)
                    stand.delete()
                msg = 'Площадка была успешно удалена'
                if len(names)>1:
                    msg = 'Площадки были успешно удалены'
                response = {'error': {'code': 0, 'message': msg}, 'content': {'names': names}}
                return HttpResponse(json.dumps(response), content_type='application/json')
            except:
                msg = 'При удалении площадки что-то пошло не так, площадка не была удалена'
                if len(names)>1:
                    msg = 'При удалении площадок что-то пошло не так, площадки не были удалены'
                response = {'error': {'code': 1, 'message': msg}}
                return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            return
    else:
        return
