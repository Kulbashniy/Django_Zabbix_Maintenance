from django.contrib import admin
from app.models import *

class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin')

class HostAdmin(admin.ModelAdmin):
    list_display = ('zabbix_id', 'name', 'zabbix', 'display_host_group', 'stand')

class Host_groupAdmin(admin.ModelAdmin):
    list_display = ('zabbix_id', 'name', 'zabbix')

class StandAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_host')

class Maintenance_modeAdmin(admin.ModelAdmin):
    list_display = ('person', 'create_time', 'status', 'start_time', 'end_time')
    exclude = ['status']

admin.site.register(Person, PersonAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Host_group, Host_groupAdmin)
admin.site.register(Stand, StandAdmin)
admin.site.register(Maintenance_mode, Maintenance_modeAdmin)