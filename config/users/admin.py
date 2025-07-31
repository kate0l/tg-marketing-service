from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PartnerProfile


class PartnerProfileInline(admin.StackedInline):
    model = PartnerProfile
    extra = 0
    fields = ('status', 'balance', 'partner_since', 'payment_details')
    readonly_fields = ('partner_since',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_staff', 'is_partner')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    # Обновленные fieldsets с правильным именем поля avatar_image
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar_image', 'bio')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def is_partner(self, obj):
        return hasattr(obj, 'partner_profile') and obj.partner_profile.status == 'active'

    is_partner.boolean = True
    is_partner.short_description = 'Партнер'


admin.site.register(User, CustomUserAdmin)
admin.site.register(PartnerProfile)
