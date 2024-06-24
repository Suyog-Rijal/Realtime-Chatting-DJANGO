from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModel, Tokens, Friendship


class CustomUserAdmin(UserAdmin):
    model = UserModel
    list_display = ('id', 'email','firstname', 'lastname', 'gender', 'last_seen', 'online_status', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('firstname', 'lastname', 'dob', 'gender', 'address', 'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'firstname', 'lastname', 'is_staff', 'is_active', 'is_verified')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class TokensAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'expiry_date')


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_1', 'user_2', 'status', 'date_added')


admin.site.register(UserModel, CustomUserAdmin)
admin.site.register(Tokens, TokensAdmin)
admin.site.register(Friendship, FriendshipAdmin)
