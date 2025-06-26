from django.contrib import admin
from .models import CastMember

# Register your models here.
@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('type',)
