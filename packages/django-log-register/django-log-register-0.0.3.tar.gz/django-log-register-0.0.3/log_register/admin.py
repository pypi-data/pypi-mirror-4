from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from log_register.models import Lot, Log
from django.core.urlresolvers import reverse


def url_to_edit_object(obj):
    content_type = ContentType.objects.get_for_model(obj)
    url = reverse('admin:%s_%s_change' % (content_type.app_label, content_type.model),  args=[obj.id])
    return u'<a href="%s">%s</a>' % (url,  obj.__unicode__())


def get_url_if_define(obj):
    if obj.content_type is None or obj.object_id is None:
        return "<(Not registered)>"
    else:
        content_type = obj.content_type
        object_id = obj.object_id
        obj_to_register = content_type.get_object_for_this_type(id=object_id)
        return url_to_edit_object(obj_to_register)


class LotAdmin(admin.ModelAdmin):
    readonly_fields = (
        "register_start",
        "register_end",
    )
    list_display = (
        "register_start",
        "register_end",
    )


class LogAdmin(admin.ModelAdmin):
    readonly_fields = (
        "reason",
        "extra_data",
    )
    list_display = (
        "reason",
        "extra_data",
    )

admin.site.register(Lot, LotAdmin)
admin.site.register(Log, LogAdmin)

__author__ = 'leandro'
