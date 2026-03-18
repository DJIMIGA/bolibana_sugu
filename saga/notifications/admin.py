from django.contrib import admin
from .models import PushToken


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'updated_at')
