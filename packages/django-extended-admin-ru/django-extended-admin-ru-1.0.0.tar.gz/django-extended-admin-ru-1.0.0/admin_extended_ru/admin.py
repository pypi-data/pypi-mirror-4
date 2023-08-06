from django.contrib import admin

from .decorators import message_wrapper


class ModelAdmin(admin.ModelAdmin):
    @message_wrapper
    def message_user(self, *args, **kwargs):
        return super(ModelAdmin, self).message_user(*args, **kwargs)
