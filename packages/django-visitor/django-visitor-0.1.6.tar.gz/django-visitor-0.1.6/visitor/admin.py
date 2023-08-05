from django.contrib import admin
from visitor.models import Visitor

class VisitorAdmin(admin.ModelAdmin):
    list_display = ['visitor_key', 'num_visits', 'last_update', 'created']

admin.site.register(Visitor, VisitorAdmin)