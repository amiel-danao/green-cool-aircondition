from django.contrib import admin

from system.forms import RegisterForm


def global_context(request):
    return {
        'app_title': admin.site.site_title,
        'app_short_title': 'Green Cool',
        'app_description': 'Refrigeration Air-Conditioning Supply and Services Corporation',
        'app_schedule': 'Mon - Fri : 09.00 AM - 09.00 PM',
        'app_location': '',
        'app_contact_no': '0995-473-4825'
    }
