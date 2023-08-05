from django.contrib import admin
from models import GameTeXObject, GameTeXFieldValue, GameTeXUser

class CustomFieldInline(admin.TabularInline):
    model = GameTeXFieldValue

class GTUInline(admin.TabularInline):
    model = GameTeXUser

class GTOAdmin(admin.ModelAdmin):
    fields = ('name', 'macro', 'classes')
    readonly_fields = ('classes',)
    inlines = [CustomFieldInline, GTUInline]

admin.site.register(GameTeXObject, GTOAdmin)