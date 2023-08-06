from django.contrib import admin
from django.utils.translation import ugettext as _
from cms.admin.placeholderadmin import PlaceholderAdmin
from hvad.admin import TranslatableAdmin

from models import *

class EventCategoryAdmin(TranslatableAdmin):
    date_hierarchy = 'created'
    list_display = ('slug', '__unicode__', 'all_translations')    
    
    fieldsets = (
        ('Event category info',{
            'fields': ('name', 'slug'),
        }),
    )
    
    def __init__(self, *args, **kwargs):
        super(EventCategoryAdmin, self).__init__(*args, **kwargs)
        self.prepopulated_fields = {'slug': ('name',)}
    
    def queryset(self, request):
        return EventCategory.on_site.all()

    def save_model(self, request, obj, form, change):
        obj.save()
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        if current_site not in obj.sites.all():
            obj.sites.add(current_site)

admin.site.register(EventCategory, EventCategoryAdmin)


class EventAdmin(TranslatableAdmin, PlaceholderAdmin):
    date_hierarchy = 'start'
    list_display = ('slug', '__unicode__', 'start', 'all_translations', )
    list_filter = ('start', 'categories', )
    search_fields = ['start', ]
    filter_horizontal = ['categories']
    fieldsets = (
        ('Event info',{
            'fields': ('name', 'slug', 'start', 'description'),
        }),
        (_(u'More options...'),{
            'classes': ['collapse'],
            'fields': ( 'time', 'end', 'categories'),
        }),
    )
    
    def __init__(self, *args, **kwargs):
        super(EventAdmin, self).__init__(*args, **kwargs)
        self.prepopulated_fields = {'slug': ('name',)}
    
    def queryset(self, request):
        return Event.on_site.all()
	
    def save_model(self, request, obj, form, change):
        obj.save()
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        if current_site not in obj.sites.all():
            obj.sites.add(current_site)
            
admin.site.register(Event, EventAdmin)

