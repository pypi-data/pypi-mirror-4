# -*- coding: utf-8 -*-
from django.conf import settings


def facebook_api_key(request):
    FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', '')
    FACEBOOK_EXTENDED_PERMISSIONS = getattr(settings, 
                                            'FACEBOOK_EXTENDED_PERMISSIONS',
                                            '')
    
    if FACEBOOK_APP_ID:
        return {'FACEBOOK_APP_ID': FACEBOOK_APP_ID,
                'login_button_perms': ','.join(FACEBOOK_EXTENDED_PERMISSIONS)}
    else:
        return {}
