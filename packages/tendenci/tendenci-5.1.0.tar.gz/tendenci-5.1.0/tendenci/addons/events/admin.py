from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.http import HttpResponseRedirect

from tendenci.addons.events.models import CustomRegForm, CustomRegField, Registrant, Type
from tendenci.addons.events.forms import CustomRegFormAdminForm, CustomRegFormForField, TypeForm
from tendenci.core.event_logs.models import EventLog

class EventAdmin(admin.ModelAdmin):
#    form = EventForm
    list_display=(
        'title',
        'description',
        'group',
        'start_dt',
        'end_dt',
        'timezone',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',
        'status',
        'status_detail',
    )

# admin.site.register(Event, EventAdmin)
# admin.site.register(Type)
# admin.site.register(Registrant)

class EventTypeAdmin(admin.ModelAdmin):
    form = TypeForm
    list_display=(
        'name',
        'bg_color',
        'reassign',
    )

    def reassign(self, obj):

        return """<a href="%s">Reassign all events from this type</a>
            """ % (reverse('event.reassign_type', args=[obj.id]))
    reassign.allow_tags = True
    reassign.short_description = 'Reassign Link'

    class Media:
        css = {'all': ['%scss/admin/event-types-color-set.css' % settings.STATIC_URL], }

admin.site.register(Type, EventTypeAdmin)

class CustomRegFieldAdminForm(CustomRegFormForField):
    class Meta:
        model = CustomRegField

    
class CustomRegFieldAdmin(admin.TabularInline):
    model = CustomRegField    
    form = CustomRegFieldAdminForm
    extra = 0
    verbose_name = 'custom field'
    ordering = ("position",)
    template = "events/admin/tabular.html"
    
def clone_forms(modeladmin, request, queryset):
    for form in queryset:
        cloned = form.clone()
        cloned.name = 'Clone of %s' % cloned.name
        cloned.save()
        
clone_forms.short_description = 'Clone selected forms'

class CustomRegFormAdmin(admin.ModelAdmin):
    inlines = (CustomRegFieldAdmin,)
    list_display = ("name", "preview_link", "for_event", "notes", "status",)
    search_fields = ("name", "notes", "status",)
    fieldsets = (
        (None, {"fields": ("name", "notes", 'status')}),
        ('Add fields to your form', {'fields': (('first_name', 'last_name', 'email'),
                                                 ('company_name', 'phone', 'position_title'),
                                                 ('address', 'city', 'state'),
                                                 ('zip', 'country', 'meal_option'), 
                                                 ('comments')),
                                     'classes': ('mapped-fields',),
                                     'description': 'The fields you selected will be automatically added to ' + \
                                     'your form. These fields are mapped to the user fields in ' + \
                                     'the registration. To delete a mapped field, uncheck its corresponding ' + \
                                     'check box here. Please do not add another custom field ' + \
                                     'if you can find a field here. To add a custom field, click Add a ' + \
                                     'Custom Field in the Fields section below.'})
    )
    #readonly_fields = ['event']
    
    form = CustomRegFormAdminForm
    actions = [clone_forms]
    
    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            #'%sjs/admin/form-fields-inline-ordering.js' % settings.STATIC_URL,
            '%sjs/admin/custom_reg_form_inline_ordering.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }
        
    def preview_link(self, obj):

        return """<a href="%s">preview</a>
            """ % (reverse('event.custom_reg_form_preview', args=[obj.id]))
    preview_link.allow_tags = True
    preview_link.short_description = 'Preview Link'
    
    def for_event(self, obj):
        event = None
        regconf = obj.regconfs.all()[:1]
        if regconf:
            event = regconf[0].event
        regconfpricing = obj.regconfpricings.all()[:1]
        if regconfpricing:
            event = regconfpricing[0].reg_conf.event
        if event:
            return """<a href="%s">%s(ID:%d)</a>
            """ % (reverse('event', args=[event.id]), event.title, event.id)
        return ''
        
    for_event.allow_tags = True
    for_event.short_description = 'For Event'
    
#    def get_fieldsets(self, request, instance=None):
#        """
#        Dynamically generate the fieldset
#        """
#        fields = ['name', 'notes', 'status']
##        if instance and instance.entries.count():
##            
##            # used - indicate the form has been used or is being used
##            fields.append('used')
#
#        field_list = ((None, {'fields': tuple(fields)}),)
#
#        return field_list

    def change_view(self, request, object_id, extra_context=None):
        result = super(CustomRegFormAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

        
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            
        instance.owner = request.user
        instance.owner_username = request.user.username

        # save the object
        instance.save()
        
        form.save_m2m()
        
        return instance
    
    def log_deletion(self, request, object, object_repr):
        super(CustomRegFormAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 176300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(instance=object)
    
    def log_change(self, request, object, message):
        super(CustomRegFormAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 176200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
    
    def log_addition(self, request, object):
        super(CustomRegFormAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 176100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)


admin.site.register(CustomRegForm, CustomRegFormAdmin)
