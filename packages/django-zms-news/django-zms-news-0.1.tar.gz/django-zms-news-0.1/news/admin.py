from django.contrib import admin
from models import New

class NewAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    class Media:
        js = (
            'js/jquery.min.js',
            'js/jquery-ui.min.js',
        )

admin.site.register(New, NewAdmin)