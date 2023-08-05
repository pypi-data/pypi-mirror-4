"""
Contains all ModelAdmins for django_shawty
"""

from django.contrib import admin
from .models import ShawtyURL

class ShawtyURLAdmin(admin.ModelAdmin):
    """
    ModelAdmin for the Shawty URL model
    """

    shawty_fieldset = (
        'Shawty Short URL Information',
        { 'fields':
              (
                  'short_url_id',
                  'short_url',
                  'long_url',
                  'created_date',
                  'modified_date',
                  ),
          'classes': ['extrapretty', 'wide'],
          }
        )

    fieldsets = (shawty_fieldset, )

    list_display = ('id', 'short_url_id',
                    'short_url', 'long_url',
                    'created_date', 'modified_date')

    list_display_links = list_display

    search_fields = ('=id', 'short_url_id', 'short_url', 'long_url')

    readonly_fields = list_display

admin.site.register(ShawtyURL, ShawtyURLAdmin)
