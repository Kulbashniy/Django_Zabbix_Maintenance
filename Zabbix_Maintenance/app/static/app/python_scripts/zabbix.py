import requests
import json
from pyzabbix import ZabbixAPI, ZabbixAPIException


class Zabbix:
    # use only as Static (u can use it as instance but it probably has error and unhandled exception)
    # only static methods and variables

    url = 'http://zabbix.sys.local'                 # url of zabbix api
    urlnet = 'http://zabbixnet.sys.local'           # url of zabbix api
    zapi = ZabbixAPI(url)                           # pyzabbix class
    zapinet = ZabbixAPI(urlnet)                     # pyzabbix class
    login = 'xxxxxx'                                # login to access zabbix api
    loginnet = 'xxxxxx'                             # login to access zabbixnet api
    password = 'xxxxxxxxx'                          # password to access zabbix api
    passwordnet = 'xxxxxxxxx'                       # password to access zabbixnet api

    ############################## NO NEEDED ################################################
    def __init__(self):
        self.login = 'xxxxxxxxxxxx'                                       
        self.password = 'xxxxxxxxxxx'                                 
        self.url = 'http://zabbix.sys.local'                       
        self.zapi = ZabbixAPI(self.url)
        self.zapi.login(self.login, self.password)
    ############################## NO NEEDED ################################################

    #def __login_before(method):
    #    # @functype - Decorator
    #    # @rtype - None(if excpetion) or function result
    #    # This decorator try log in zabbix api before send request
    #    if not Zabbix.zapi.auth:                                # field auth is string ''
    #        Zabbix.zapi.login(Zabbix.login, Zabbix.password)    # login by ZabbixAPI lib if not loged in
    #    def wrapper(*args, **kwargs):
    #        try:
    #            return method(*args, **kwargs)                  # original method return
    #        except ZabbixAPIException:
    #            try:
    #                Zabbix.zapi.login(Zabbix.login, Zabbix.password)    # try login again
    #                return method(*args, **kwargs)
    #            except:
    #                return None
    #    return wrapper

    ############################## NO NEEDED ################################################
    @classmethod
    def log_in(cls, zabbix='all', anyway=False):
        if zabbix=='all':
            if anyway:
                cls.zapi.login(cls.login, cls.password)
                cls.zapinet.login(cls.loginnet, cls.passwordnet)
            if not cls.zapi.auth:
                cls.zapi.login(cls.login, cls.password)
            if not cls.zapinet.auth:
                cls.zapinet.login(cls.loginnet, cls.passwordnet)
        elif zabbix==cls.url:
            if anyway:
                cls.zapi.login(cls.login, cls.password)
            if not cls.zapi.auth:
                cls.zapi.login(cls.login, cls.password)
        elif zabbix==cls.urlnet:
            if anyway:
                cls.zapinet.login(cls.loginnet, cls.passwordnet)
            if not cls.zapinet.auth:
                cls.zapinet.login(cls.loginnet, cls.passwordnet)


    @classmethod
    def _get_zapi_by_url(cls, zabbix):
        if zabbix==cls.url:
            return cls.zapi
        elif zabbix==cls.urlnet:
            return cls.zapinet


    @classmethod
    def _request_hosts(cls, zabbix):
        cls.log_in(zabbix)
        zapi = cls._get_zapi_by_url(zabbix)
        try:
            result = zapi.host.get(output="extend", selectGroups="extend")
            return result
        except:
            try:
                cls.log_in(zabbix, anyway=True)
                result = zapi.host.get(output="extend", selectGroups="extend")
                return result
            except:
                return None


    @classmethod
    def request_hg_with_h(cls, zabbix):

        def has_group(groupid, group_list):
            for group in group_list:
                if group.get('id') == groupid:
                    return True
            return False

        current_zabbix = zabbix[7:]
        try:
            result = list()
            rec_hosts = cls._request_hosts(zabbix)
            for host in rec_hosts:
                hostid = host['hostid']
                hostname = host['name']
                groups = host['groups']
                for group in groups:
                    groupid = group['groupid']
                    groupname = group['name']
                    if has_group(groupid, result):
                        for idx, hg in enumerate(result):
                            if hg.get('id') == groupid:
                                result[idx].get('hosts').append({'id': hostid, 'name': hostname, 'zabbix': current_zabbix})
                    else:
                        result.append({'id': groupid, 'name': groupname, 'zabbix': current_zabbix, 'hosts': [{'id': hostid, 'name': hostname, 'zabbix': current_zabbix}]})
            return result
        except:
            return None

    @classmethod
    def get_hg_with_h(cls):
        # @rtype - list of host_groups with attached hosts or None by decorator
        # @return - [ { 'id': '@host_group_id', 'name': '@host_group_name', 'zabbix': @zabbixurl, 'hosts': [{'id': '@host_id', 'name': '@host_name', 'zabbix': @zabbixurl}, ...] }, ...]
        # @return - or None
        result = cls.request_hg_with_h(cls.url)
        if result == None:
            result = cls.request_hg_with_h(cls.urlnet)
        else:
            resultnet = cls.request_hg_with_h(cls.urlnet)
            if resultnet != None:
                result.extend(resultnet)
        return result


    @classmethod
    def _request_create_mm(cls, zabbix, **kwargs):
        # kwargs must include 'desciption', 'name', 'start', 'end', 'hostids'
        # 'start' and 'end' - is timestamp
        timeperiods = [{
            'period': kwargs['end']-kwargs['start'],                        # duration mm in seconds
            'start_date': kwargs['start'],                                  # timestamp of start mm
            'timeperiod_type': 0                                            # type of mm (0-once, 2-daily, 3-weekly,4-monthly)
        }]
        zapi = cls._get_zapi_by_url(zabbix)
        cls.log_in(zabbix)                                                  # log in if not logged
        try:
            response = zapi.maintenance.create(name=kwargs['name'], active_since=kwargs['start'], active_till=kwargs['end'], description=kwargs['description'], hostids=kwargs['hostids'], timeperiods=timeperiods)
            if 'maintenanceids' in response:                                # if hasn't maintenanceids in response Fail return False
                return True
            else:                                                           # else then response has maintenanceids in response Success return True
                return False
        except:
            cls.log_in(zabbix, anyway=true)                                         # log in again anyway
            response = zapi.maintenance.create(name=kwargs['name'], active_since=kwargs['start'], active_till=kwargs['end'], description=kwargs['description'], hostids=kwargs['hostids'], timeperiods=timeperiods)
            if 'maintenanceids' in response:                                # if hasn't maintenanceids in response Fail return False
                return True
            else:                                                           # else then response has maintenanceids in response Success return True
                return False


    @classmethod
    def create_mm(cls, **kwargs):
        # kwargs must include 'desciption', 'name', 'start', 'end', 'hostids'
        # 'hostids' - is [{'id': @id, 'zabbix': @zabbixurl}, ...]
        # 'start' and 'end' - is timestamp
        hostids = list()
        for host in kwargs.get('hostids'):
            if host['zabbix'] == cls.url[7:]:
                hostids.append(host['id'])
        hostidsnet = list()
        for host in kwargs.get('hostids'):
            if host['zabbix'] == cls.urlnet[7:]:
                hostidsnet.append(host['id'])
        zabbix = cls.url
        zabbixnet = cls.urlnet
        result = {'error': {'code': 0, 'message': 'Режим успешно создан'}}
        if len(hostids):
            if cls._request_create_mm(zabbix, name=kwargs['name'], start=kwargs['start'], end=kwargs['end'], description=kwargs['description'], hostids=hostids):
                if len(hostidsnet):
                    if not cls._request_create_mm(zabbixnet, name=kwargs['name'], start=kwargs['start'], end=kwargs['end'], description=kwargs['description'], hostids=hostidsnet):
                        result = {'error': {'code': 11, 'message': 'Режим обслуживания для ' + zabbixnet[7:] + ' не был создан, однако режим обслуживания для ' + zabbix[7:] + ' был создан'}}
            else:
                if len(hostidsnet):
                    if not cls._request_create_mm(zabbixnet, name=kwargs['name'], start=kwargs['start'], end=kwargs['end'], description=kwargs['description'], hostids=hostidsnet):
                        result = {'error': {'code': 12, 'message': 'Ошибка обращения к Zabbix API режим обслуживание не был создан'}}
                    else:
                        result = {'error': {'code': 13, 'message': 'Режим обслуживания для ' + zabbix[7:] + ' не был создан, однако режим обслуживания для ' + zabbixnet[7:] + ' был создан'}}
                else:
                    result = {'error': {'code': 12, 'message': 'Ошибка обращения к Zabbix API режим обслуживание не был создан'}}
        elif len(hostidsnet):
            if not cls._request_create_mm(zabbixnet, name=kwargs['name'], start=kwargs['start'], end=kwargs['end'], description=kwargs['description'], hostids=hostidsnet):
                result = {'error': {'code': 12, 'message': 'Ошибка обращения к Zabbix API режим обслуживание не был создан'}}
        return result



    @classmethod
    def logout(cls):
        cls.zapi.user.logout()


    @staticmethod
    def validate_auth(login, password):
        try:
            zapi = ZabbixAPI('http://zabbix.sys.local')
            zapi.login(login, password)
            zapi.user.logout()
            return True
        except:
            return False
