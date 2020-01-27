"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.db import IntegrityError


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)     # set the default user to person
    admin = models.BooleanField(default=False)                      # role of person(access to Stands)
    login = models.CharField(null=True, max_length=100)             # User login

    def get_mm(self):
        # get query_dict of all Maintence_mods provided this person
        qs_mm = self.person_mms.all()
        if qs_mm.exists():
            cur_time = datetime.now(tz=qs_mm.first().end_time.tzinfo)
            for mm in qs_mm:
                # set current status of all Mms
                if cur_time>mm.end_time:
                    if mm.status!='Завершено':
                        mm.status = 'Завершено'
                        mm.save()
                elif cur_time > mm.start_time and cur_time < mm.end_time:
                    if mm.status!='Активно':
                        mm.status = 'Активно'
                        mm.save()
                elif cur_time < mm.start_time:
                    if mm.status!='Неактивно':
                        mm.status = 'Неактивно'
                        mm.save()
            return qs_mm

    def set_admin(self):
        # set admin field to true
        self.admin = True
        self.save()

    def is_admin(self):
        # check person is admin
        # @rtype - bool
        return self.admin

    def set_data(self, **kwargs):
        if 'login' in kwargs:
            self.login = kwargs.get('login')
        self.save()

    def __str__(self):
        return self.user.__str__()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):               # Create Person if User created
    if created:
        if Person.objects.filter(user=instance):                            # if person already exists
            return
        else:
            Person.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):                          # Save Person if User saved
    instance.person.save()


class Stand(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)                    # Name of stand
    
    def __str__(self):
        return self.name

    def get_hosts(self):
        self.refresh_from_db()
        return self.host_stand.all()                                                # return all hosts in this stand

    def get_hosts_list(self):
        self.refresh_from_db()
        return list(self.host_stand.values_list('name', flat=True))                 # return list names of host in this stand

    def get_host_list_ids(self, refresh=False):
        if refresh:
            self.refresh_from_db()
        return list(self.host_stand.values_list('id', flat=True))                   # return list ids of host in this stand

    def get_host_list_zabbix_and_ids(self, refresh=False):
        if refresh:
            self.refresh_from_db()
        result = list()
        for host in self.host_stand.all():
            result.append({'id': host.zabbix_id, 'zabbix': host.zabbix})
        return result

    def display_host(self):
        # display host groups in Admin Panel
        return ', '.join([ host.name for host in self.host_stand.all() ])
    display_host.short_description = 'Hosts'

    def update(self, *args, **kwargs):
        if 'name' in kwargs and 'hg_h' in kwargs:
            try:
                # Check all hosts, probably they have stand already
                for host_group in kwargs.get('hg_h'):
                    for host in host_group.get('hosts'):
                        host_obj = Host.objects.filter(zabbix_id=int(host.get('id')), zabbix=host.get('zabbix'))          # get Host by id
                        if len(host_obj):                                               # if has host_obj
                            qs = Stand.objects.filter(host_stand=host_obj[0])
                            if len(qs):       # check stand with that host already exists exclude
                                qs = qs.exclude(pk=self.pk)
                                if qs.exists():
                                    return 'Площадка с хостом '+str(host_obj[0].name) +' уже существует'
                self.name = kwargs.get('name')
                self.save()
                self.host_stand.all().update(stand=None)                                # Убираем у всех хостов наш стенд(площадку)
                for host_group in kwargs.get('hg_h'):
                    hg_obj, created_hg = Host_group.objects.get_or_create(zabbix_id=int(host_group.get('id')), zabbix=host_group.get('zabbix'))
                    if created_hg:
                        # Если создали новую хост группу запишем ее имя
                        hg_obj.name = host_group.get('name')
                        hg_obj.save(update_fields=['name'])
                    for host in host_group.get('hosts'):
                        host_obj, created_h = Host.objects.get_or_create(zabbix_id=int(host.get('id')), zabbix=host.get('zabbix'))
                        if created_h:
                            # Если создали новый хост запишем его имя
                            host_obj.name = host.get('name')
                            host_obj.save(update_fields=['name'])
                            host_obj.host_group.add(hg_obj)                             # set host group to host
                        host_obj.stand = self                                           # update owner of host in stands
                        host_obj.save()
            except IntegrityError as e:
                if 'unique constraint' in e.__str__().lower():
                    return 'Площадка с таким именем уже существует'
                else:
                    return 'При изменении записи в БД что-то пошло не так'
            except:
                return 'Переданные аргументы имеют некорректную структуру'
            


    def save(self, *args, **kwargs):
        # check hosts add availability to stands
        if 'hg_h' in kwargs:
            try:
                # Check all hosts, probably they have stand already
                for host_group in kwargs.get('hg_h'):
                    for host in host_group.get('hosts'):
                        host_obj = Host.objects.filter(zabbix_id=int(host.get('id')), zabbix=host.get('zabbix'))    # get Host by id
                        if len(host_obj):                                                                           # if has host_obj
                            if len(Stand.objects.filter(host_stand=host_obj[0])):                                   # check stand with that host already exists
                                return 'Площадка с хостом - '+str(host_obj[0].name) +' из ' + str(host_obj[0].zabbix) + ' уже существует'
                
                super(Stand, self).save()
                
                for host_group in kwargs.get('hg_h'):
                    hg_obj, created_hg = Host_group.objects.get_or_create(zabbix_id=int(host_group.get('id')), zabbix=host_group.get('zabbix'))
                    if created_hg:
                        # Если создали новую хост группу запишем ее имя
                        hg_obj.name = host_group.get('name')
                        hg_obj.save(update_fields=['name'])
                    for host in host_group.get('hosts'):
                        host_obj, created_h = Host.objects.get_or_create(zabbix_id=int(host.get('id')), zabbix=host.get('zabbix'))
                        if created_h:
                            # Если создали новый хост запишем его имя
                            host_obj.name = host.get('name')
                            host_obj.save(update_fields=['name'])
                            host_obj.host_group.add(hg_obj)                             # set host group to host
                        host_obj.stand = self                                           # update owner of host in stands
                        host_obj.save()
            except IntegrityError as e:
                if 'unique constraint' in e.__str__().lower():
                    return 'Площадка с таким именем уже существует'
                else:
                    return 'При создании записи в БД что-то пошло не так'
            except:
                return 'Переданные аргументы имеют некорректную структуру'
        else:
            super(Stand, self).save(*args, **kwargs)

    


class Host(models.Model):
    zabbix_id = models.IntegerField(null=False)                             # Zabbix host id
    name = models.CharField(null=True, max_length=100)                      # Name of host
    zabbix = models.CharField(null=False, max_length=50)                    # Zabbix url (without http://)
    host_group = models.ManyToManyField('Host_group', related_name='host_group_hosts')     # key to host_group that contain this host
    stand = models.ForeignKey(Stand, on_delete=models.SET_NULL, blank=True, null=True, related_name='host_stand')

    def __str__(self):
        return self.name

    def display_host_group(self):
        # display host groups in Admin Panel
        return ', '.join([ host_group.name for host_group in self.host_group.all() ])
    display_host_group.short_description = 'Host_groups'

class Host_group(models.Model):
    zabbix_id = models.IntegerField(null=False)                             # Zabbix host_group id   
    name = models.CharField(null=True, max_length=100)                      # Name of host_group
    zabbix = models.CharField(null=False, max_length=50)                    # Zabbix url (without http://)


    def get_hosts(self):
        # return query_dict of all host contain in this host_group
        hosts = self.host_group_hosts.all()
        return hosts

    def __str__(self):
        return self.name



class Maintenance_mode(models.Model):
    person = models.ForeignKey(Person, on_delete = models.CASCADE, null=False, related_name='person_mms')  # Use FK to setup relationship one user(Person) multiply MM
    create_time = models.DateTimeField(auto_now=True, null=False)                       # time of create this MM
    status = models.CharField('Current status', null=False, max_length=20, blank=True)  # Активно/неактивно/завершено
    start_time = models.DateTimeField(null=False)                                       # Start period MM
    end_time = models.DateTimeField(null=False)                                         # End period MM
    hosts = models.ManyToManyField(Host, blank=True)                                    # Use ManyToMany to setup relationship Multiply Host to multiply MM
    stands = models.ManyToManyField(Stand, blank=True)                                  # Use ManyToMany to setup relationship Multiply Stand to multiply MM

    def save(self, *args, **kwargs):
        # set status when save Mm
        dt_now = datetime.now(tz=self.start_time.tzinfo)
        if self.start_time <= dt_now and self.end_time > dt_now:
            self.status = 'Активно'
        elif self.start_time > dt_now:
            self.status = 'Неактивно'
        elif self.end_time <= dt_now:
            self.status = 'Завершено'
        super(Maintenance_mode, self).save(*args, **kwargs) 

    def get_hosts(self):
        hosts = ', '.join([host.name for host in self.hosts.all()])
        stands= ', '.join([stand.name for stand in self.stands.all()])
        return hosts+stands

    def set_mm_hosts(self, *args,**kwargs):
        # needed hg_with_h or stands in kwargs
        if 'hg_with_h' in kwargs:
            for host_group in kwargs.get('hg_with_h'):
                hg_obj, created_hg = Host_group.objects.get_or_create(zabbix_id=int(host_group.get('id')), zabbix=host_group.get('zabbix'))
                if created_hg:
                    # Если создали новую хостгруппу запишем ее имя
                    hg_obj.name = host_group.get('name')
                    hg_obj.save(update_fields=['name'])
                for host in host_group.get('hosts'):
                    host_obj, created_h = Host.objects.get_or_create(zabbix_id=int(host.get('id')), zabbix=host.get('zabbix'))
                    if created_h:
                        # Если создали новый хост запишем его имя
                        host_obj.name = host.get('name')
                        host_obj.save(update_fields=['name'])
                        host_obj.host_group.add(hg_obj)                             # set host group to host
                    self.hosts.add(host_obj)                                        # add host to MM
        elif 'stands' in kwargs:
            for stand in kwargs.get('stands'):
                stand_obj = Stand.objects.get(id=int(stand.get('id')))
                self.stands.add(stand_obj)




