from django.contrib import admin

# Register your models here.
from .models import Group

# Register your models here.


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_editorial', 'order', 'owner')
    list_filter = ('is_editorial',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    filter_horizontal = ('channels',)
