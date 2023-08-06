# -*- coding: utf-8 -*-
from django.contrib import admin
from vkontakte_api.admin import VkontakteModelAdmin
from vkontakte_groups.admin import Group, GroupAdmin as GroupAdminOriginal
from models import GroupStat

class GroupStatInline(admin.TabularInline):
    model = GroupStat
    fields = ('date','visitors','views','likes','comments','shares','new_members','ex_members','members','ads_visitors','ads_members','males','females')
    readonly_fields = fields
    extra = 0
    can_delete = False

class GroupAdmin(GroupAdminOriginal):
    inlines = GroupAdminOriginal.inlines + [GroupStatInline]

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)