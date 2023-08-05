from django.contrib import admin
from zeropass.models import Token


class TokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = (
        'token',
        'expires',
        'user')


admin.site.register(Token, TokenAdmin)
