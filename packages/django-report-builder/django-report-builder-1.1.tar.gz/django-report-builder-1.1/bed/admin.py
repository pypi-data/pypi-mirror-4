from django.contrib import admin
from bed.models import *

class MdlUserAdmin(admin.ModelAdmin):
    list_filter = ['some_date']
    fields = [('some_date','username')]
admin.site.register(MdlUser, MdlUserAdmin)
admin.site.register(Moo)
admin.site.register(MooBar)
