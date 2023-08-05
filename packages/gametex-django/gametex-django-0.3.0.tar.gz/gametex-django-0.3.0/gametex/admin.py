from django.contrib import admin
from models import GameTeXObject, GameTeXFieldValue, GameTeXUser

class CustomFieldInline(admin.TabularInline):
    """
    Inline editor for GameTeX custom fields.
    """
    model = GameTeXFieldValue

class GTUInline(admin.TabularInline):
    """
    Inline editor for GameTeX users.
    """
    model = GameTeXUser

class GTOAdmin(admin.ModelAdmin):
    """
    GameTeXObject admin.
    """
    fields = ('name', 'macro', 'classes')
    readonly_fields = ('classes',)
    inlines = [CustomFieldInline, GTUInline]

admin.site.register(GameTeXObject, GTOAdmin)
