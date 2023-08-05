from django.contrib import admin

from .import models


class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_target', 'image']


class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'score', 'target', 'achieved', 'badge']


admin.site.register(models.Badge, BadgeAdmin)
admin.site.register(models.Achievement, AchievementAdmin)
