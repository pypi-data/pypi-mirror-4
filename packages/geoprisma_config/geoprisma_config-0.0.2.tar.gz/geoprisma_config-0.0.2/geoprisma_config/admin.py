import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.admin import helpers
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.contrib.admin.util import quote
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.http import Http404, HttpResponseRedirect
from django.utils.html import escape
from django import forms, template

from geoprisma_config.models import *
from geoprisma_config.forms import *
from utils import join_url

try:
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns


# Inlines

class ServiceOptionInline(admin.TabularInline):
    form = ServiceOptionForm
    model = ServiceOption
    extra = 2

class DatastoreOptionInline(admin.TabularInline):
    form = DatastoreOptionForm
    model = DatastoreOption
    extra = 2

class ResourceFieldInline(admin.TabularInline):
    model = ResourceField
    extra = 5

class ResourceOptionInline(admin.TabularInline):
    form = ResourceOptionForm
    model = ResourceOption
    extra = 5

class FieldOptionInline(admin.TabularInline):
    form = FieldOptionForm
    model = FieldOption
    extra = 5

class AccessFilterOptionInline(admin.TabularInline):
    form = AccessFilterOptionForm
    model = AccessFilterOption
    extra = 5

class WidgetOptionInline(admin.TabularInline):
    form = WidgetOptionForm
    model = WidgetOption
    extra = 5

class MapContextOptionInline(admin.TabularInline):
    form = MapContextOptionForm
    model = MapContextOption
    extra = 5

class MapContextResourceInline(admin.TabularInline):
    model = MapContextResource
    extra = 5

class ApplicationWidgetInline(admin.TabularInline):
    model = ApplicationWidget
    extra = 5

# Admin Model

class BaseModelAdmin(admin.ModelAdmin):

    change_form_template = 'admin/change.html'

    def get_urls(self):
        urls = super(BaseModelAdmin, self).get_urls()
        my_urls = patterns('',
                          ('^(?P<object_id>\d+)/$', self.changelist_changeform_view),
                          )
        return my_urls + urls

    def changelist_changeform_view(self, request, extra_context=None, add=False, object_id=None):
        "The 'change list' and 'change form' admin view for BaseModelAdmin."
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Fix links of save, save_continue form buttons
        if not add and not object_id:
            request.path += 'add/'

        if '_popup' in request.REQUEST.keys():
            return super(BaseModelAdmin, self).add_view(request)

        # the form sender is either the changelist or the changeform
        formSender = None
        if '_formSender' in request.POST.keys():
            formSender = request.POST['_formSender']

        if request.method == 'POST' and formSender == 'changeform' and request.POST.has_key('_cancelgoback'):
            return HttpResponseRedirect('../')

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)

        # Remove action checkboxes if there aren't any actions available.
        list_display = list(self.list_display)
        if not actions:
            try:
                list_display.remove('action_checkbox')
            except ValueError:
                pass

        try:
            if django.VERSION[0:2] < (1, 4):
                cl = ChangeList(request, self.model, list_display, self.list_display_links, self.list_filter,
                                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
            else:
                cl = ChangeList(request, self.model, list_display, self.list_display_links, self.list_filter,
                                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all, self.list_editable, self)

        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk edit.
        # Try to look up an action first, but if this isn't an action the POST
        # will fall through to the bulk edit check, below.
        if actions and request.method == 'POST' and formSender == 'changelist':
            response = self.response_action(request, queryset=cl.get_query_set())
            if response:
                return response

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == "POST" and self.list_editable and formSender == 'changelist':
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        form.save_m2m()
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_unicode(opts.verbose_name)
                    else:
                        name = force_unicode(opts.verbose_name_plural)
                        msg = ungettext("%(count)s %(name)s was changed successfully.",
                                    "%(count)s %(name)s were changed successfully.",
                                        changecount) % {'count': changecount,
                                                        'name': name,
                                                        'obj': force_unicode(obj)}
                        self.message_user(request, msg)

                    return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif self.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        if django.VERSION[0:2] < (1, 4):
            root_path = self.admin_site.root_path
        else:
            root_path = request.get_full_path()

        context = {
            'model_name': force_unicode(self.model._meta.verbose_name),
            'lc': {
                'title': cl.title,
                'cl': cl,
                'media': media,
                'root_path': root_path,
                'app_label': app_label,
                },
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'is_popup': cl.is_popup,
            'has_add_permission': self.has_add_permission(request),
            'is_add': add,
            'object_id': object_id,
            }
        context.update(extra_context or {})

        if object_id:
            cl.url_for_result = lambda result, self=cl: "../%s/" % quote(getattr(result, self.pk_attname))
            return super(BaseModelAdmin, self).change_view(request, object_id,
                                                           extra_context=context)
        else:
            if add:
                cl.url_for_result = lambda result, self=cl: "../%s/" % quote(getattr(result, self.pk_attname))
            else:
                cl.url_for_result = lambda result, self=cl: "%s/" % quote(getattr(result, self.pk_attname))
            return super(BaseModelAdmin, self).add_view(request, extra_context=context)


    # Redirect standard views
    def changelist_view(self, request, extra_context=None):
        return self.changelist_changeform_view(request)

    def change_view(self, request, object_id, extra_context=None):
        return self.changelist_changeform_view(request)

    def add_view(self, request, form_url='', extra_context=None):
        return self.changelist_changeform_view(request, add=True)

class ServiceAdmin(BaseModelAdmin):
    form = ServiceForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (ServiceOptionInline,)

class DatastoreAdmin(BaseModelAdmin):
    form = DatastoreForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (DatastoreOptionInline,)


class ResourceAdmin(BaseModelAdmin):
    form = ResourceForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (ResourceOptionInline, ResourceFieldInline)
    filter_horizontal = ('datastores',)

    class Media:
        js = (
            join_url(settings.STATIC_URL,'gc_js/jquery-ui-1.8.2.custom.min.js'),
            join_url(settings.STATIC_URL,'gc_js/admin-list-reorder.js'),
        )

class FieldAdmin(BaseModelAdmin):
    form = FieldForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (FieldOptionInline,)

class AccessFilterAdmin(BaseModelAdmin):
    form = AccessFilterForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (AccessFilterOptionInline,)

class WidgetAdmin(BaseModelAdmin):
    form = WidgetForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (WidgetOptionInline,)

    class Media:
        js = (
            join_url(settings.STATIC_URL,'gc_js/jquery-ui-1.8.2.custom.min.js'),
            join_url(settings.STATIC_URL,'gc_js/admin-list-reorder.js'),
            join_url(settings.STATIC_URL,'gc_js/admin-widgets.js'),
        )

class MapContextAdmin(BaseModelAdmin):
    form = MapContextForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (MapContextOptionInline, MapContextResourceInline)

    class Media:
        js = (
            join_url(settings.STATIC_URL,'gc_js/jquery-ui-1.8.2.custom.min.js'),
            join_url(settings.STATIC_URL,'gc_js/admin-list-reorder.js'),
        )

class ApplicationAdmin(BaseModelAdmin):
    form = ApplicationForm
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (ApplicationWidgetInline,)

    class Media:
        js = (
            join_url(settings.STATIC_URL,'gc_js/jquery-ui-1.8.2.custom.min.js'),
            join_url(settings.STATIC_URL,'gc_js/admin-list-reorder.js'),
            )

class SessionAdmin(BaseModelAdmin):
    form = SessionForm
    list_display = ('name',)
    search_fields = ('name',)
    pass # do not remove this class

admin.site.register(Datastore, DatastoreAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(AccessFilter, AccessFilterAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(MapContext, MapContextAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Session, SessionAdmin)
