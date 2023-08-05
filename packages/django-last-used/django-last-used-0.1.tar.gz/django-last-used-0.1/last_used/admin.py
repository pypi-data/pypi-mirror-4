
from django.contrib import admin

from models import LastUsed


class LastUsedAdmin(admin.ModelAdmin):

    search_fields = ('user__username', 'content_type__name')
    list_filter = ('last_used', 'key', 'content_type')

    list_display = ('user', 'content_type', 'content_object', 'last_used')


admin.site.register(LastUsed, LastUsedAdmin)
