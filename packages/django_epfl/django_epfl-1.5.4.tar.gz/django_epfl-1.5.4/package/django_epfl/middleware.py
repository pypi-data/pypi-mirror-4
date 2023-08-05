# -*- coding: utf8 -*-
'''
Created on 27 févr. 2012

@author: Romain Gehrig (romain.gehrig@epfl.ch)
'''

from django import http
from django.utils.translation import check_for_language, activate

class I18nMiddleware(object):
    """
    Change the language if it intercepts the 'ln' variable in the GET method.
    """
    def process_request(self, request):
        
        # Code adapted from django.views.i18n
        if request.method == 'GET':
            lang_code = request.GET.get('ln', None)
            
            if lang_code and check_for_language(lang_code):
                activate(request.GET['ln'])
                
                # Write in the session variable or in a cookie
                if hasattr(request, 'session'):
                    request.session['django_language'] = lang_code
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        
        return None