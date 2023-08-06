from django.contrib import admin
from models import *

class EntryAdmin(admin.ModelAdmin):
    exclude = ('slug','created','uid','modified','comment_count','excerpt','views','versions','calculated_score',)
    list_display = ('author', 'title', 'start_date', 'comments_on',)
    search_fields = ('title', 'content',)

admin.site.register(Entry, EntryAdmin)
