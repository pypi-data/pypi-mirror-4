from django.contrib import admin

from . import models


class SeriesAdmin(admin.ModelAdmin):
    model = models.Series

    prepopulated_fields = {
        'slug': ('title', ),
    }


admin.site.register(models.Series, SeriesAdmin)
