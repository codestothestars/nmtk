from django.contrib import admin
from django import forms
import models
from django.utils.safestring import mark_safe
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple

# Remove DJcelery admin components.
from django.contrib import admin
from djcelery.models import (TaskState, WorkerState,
                             PeriodicTask, IntervalSchedule, CrontabSchedule)
from registration.models import (RegistrationProfile,)
from django.contrib.sites.models import (Site)
from tastypie.models import (ApiKey,)

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(RegistrationProfile)
admin.site.unregister(Site)
admin.site.unregister(ApiKey)

# class ToolConfigAdmin(admin.TabularInline):
#    model=models.ToolConfig
#    extra=0
#    max_num=1
#
#    readonly_fields=['json_config_pretty',]
#    fields=('json_config_pretty',)


class ToolServerForm(forms.ModelForm):
    resend_email = forms.BooleanField(
        required=False, label="Re-send Tool Configuration Email")
    authorized_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple(
            "Users", is_stacked=False),

        queryset=get_user_model().objects.all())

    def save(self, commit=True):
        resend_email = self.cleaned_data.get('resend_email', None)
        instance = super(ToolServerForm, self).save(commit=commit)
        if resend_email:
            instance.send_email = True
        return instance


class ToolAdminForm(forms.ModelForm):
    authorized_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple(
            "Users", is_stacked=False),
        queryset=get_user_model().objects.all())


#
# class ToolServerAuthorizedUsersInline(admin.TabularInline):
#     model = ToolServer.authorized_users.through


class ToolServerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by',)
    list_display = ['name', 'tool_server_id', 'active', ]
    form = ToolServerForm
#     inlines = [ToolServerAuthorizedUsersInline]

    def save_model(self, request, instance, form, change):
        user = request.user
        if not change:
            instance.created_by = user
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        return instance

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data['created_by'] = request.user.id
        request.GET = data
        return super(
            ToolServerAdmin,
            self).add_view(
            request,
            form_url="",
            extra_context=extra_context)


class ToolAdmin(admin.ModelAdmin):
    form = ToolAdminForm

    def json_configuration(self, obj):
        '''
        Return the web-safe json config...
        '''
        return ("""%s"""
                % (json.dumps(obj.toolconfig.json_config,
                              sort_keys=True,
                              separators=(',', ': ')
                              ),))

    readonly_fields = (
        'tool_path',
        'tool_server',
        'name',
        'json_configuration',
    )

    class Media:
        js = ("NMTK_server/admin/js/jquery-2.2.0.min.js",
              "NMTK_server/admin/js/tree.jquery.js",)
        css = {"tree": ("NMTK_server/admin/css/jqtree.css",)
               }


class JobAdmin(admin.ModelAdmin):

    def job_result_status(self, obj):
        return obj.get_status_display()

    list_filter = ['status', 'user']
    list_display = [
        'tool',
        'date_created',
        'status',
        'user',
        'job_result_status']
    fields = [
        'tool',
        'date_created',
        'status',
        'job_result_status',
        'config',
        'user',
    ]
    readonly_fields = (
        'tool',
        'status',
        'config',
        'job_result_status',
        'date_created',
    )

    def save_model(self, request, instance, form, change):
        user = request.user
        if not change:
            instance.user = user
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        return instance

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data['user'] = request.user.id
        request.GET = data
        return super(
            JobAdmin,
            self).add_view(
            request,
            form_url="",
            extra_context=extra_context)


class JobStatusAdmin(admin.ModelAdmin):
    list_display = ['job', 'timestamp', 'message']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'uri', 'date_created']


class PageContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'order', 'enabled', 'modified']


class PageNameAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']


class ToolSampleFileAdmin(admin.ModelAdmin):
    list_display = ['tool__name', 'namespace']
    readonly_fields = fields = (
        'tool',
        'namespace',
        'file_name',
        'checksum',
        'content_type',
    )

    def tool__name(self, obj):
        return obj.tool.name


class ToolSampleConfigAdmin(admin.ModelAdmin):
    list_display = ['tool__name', ]
    readonly_fields = (
        'tool',
    )

    def tool__name(self, obj):
        return obj.tool.name


class DataFileAdmin(admin.ModelAdmin):
    #    def data_file(self, obj):
    #        '''
    #        Used by the admin to provide a nice download URL.
    #        '''
    #        return mark_safe('''<a href="%s">%s</a>''' % (obj.url,
    #                                                      obj.name))
    #
    #    def data_file_geojson(self, obj):
    #        return mark_safe('''<a href="%s">%s</a>''' % (obj.geojson_url,
    #                                                      obj.geojson_name))
    list_display = ['id', 'user', 'date_created',
                    'feature_count', 'status']
    list_filter = ['user', ]
    fields = ['user', 'date_created',
              #'data_file','data_file_geojson',
              'content_type',
              'name',
              'status', 'status_message', 'srid', 'srs', 'feature_count',
              'extent', 'geom_type',
              'description']
    readonly_fields = fields[1:-1]

    def save_model(self, request, instance, form, change):
        user = request.user
        if not instance.user:
            instance.user = user
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        return instance

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data['user'] = request.user.id
        request.GET = data
        return super(
            DataFileAdmin,
            self).add_view(
            request,
            form_url="",
            extra_context=extra_context)


class MapColorStyleAdmin(admin.ModelAdmin):
    list_display = ['id', 'ramp_graphic_tag', 'description', 'default']
    readonly_fields = ('ramp_graphic_tag',)
    fieldsets = (
        (None, {
            'fields': ('ramp_graphic_tag',
                       'description',
                       'name',
                       'default',
                       'category')
        }),
        ('Unmatched Features Color', {
            'fields': (('other_r', 'other_g', 'other_b',),)
        })

    )


admin.site.register(models.PageContent, PageContentAdmin)
admin.site.register(models.PageName, PageNameAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.ToolServer, ToolServerAdmin)
admin.site.register(models.Tool, ToolAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.JobStatus, JobStatusAdmin)
admin.site.register(models.DataFile, DataFileAdmin)
admin.site.register(models.ToolSampleFile, ToolSampleFileAdmin)
admin.site.register(models.ToolSampleConfig, ToolSampleConfigAdmin)
admin.site.register(models.MapColorStyle, MapColorStyleAdmin)

# admin.site.register(models.ToolConfig, admin.ModelAdmin)
