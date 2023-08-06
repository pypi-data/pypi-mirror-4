from django.contrib import admin
from models import Query

class QueryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description', 'sql']

admin.site.register(Query, QueryAdmin)
