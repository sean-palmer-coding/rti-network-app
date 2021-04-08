from django.contrib import admin
from speedtest import models

# Register your models here.


@admin.register(models.TestResult, models.Locations)
class AuthorAdmin(admin.ModelAdmin):
    pass
