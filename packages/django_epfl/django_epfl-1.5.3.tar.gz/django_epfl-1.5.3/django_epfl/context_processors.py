'''
Created on 23 febr. 2012

@author: Romain Gehrig (romain.gehrig@epfl.ch)
'''
from django.conf import settings

def site_name(request):
    try :
        return {'SITE_NAME': settings.__getattr__('SITE_NAME')}
    except AttributeError:
        return {'SITE_NAME': None}