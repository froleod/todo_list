from django.contrib import admin
from .models import Todo


class TodoAdmin(admin.ModelAdmin):  # для отображения поля времени созданяи туду
    readonly_fields = ('created',)


admin.site.register(Todo, TodoAdmin)
