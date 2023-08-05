from setuptools import setup, find_packages

version = '1.5.0'

LONG_DESCRIPTION = """
    django_epfl
    ***********
    
    This page will talk about the EPFL templates for django. These templates have 
    been developed in order to reflect the "web2010" `Link graphical chart of EPFL <http://atelierweb.epfl.ch/charte-graphique>`.
    
    To use these templates, add ``django_epfl`` to your ``INSTALLED_APPS``. Then you
    can inherit the base template by adding ``{% extends 'django_epfl/base.html' %}``
    in a template.
    
    List of available blocks
    ========================
    
    All the following blocks are in the EPFL template. Each block is displayed in 
    its context and has its role description next to it.
    
    *  <html>
    
    *  <head>
    
    *  **additional_meta**  :  Place here all the additional meta in the 
    HTML form
    *  **additional_links** : Same for the links to additional resources
    *  **additional_css**   : Here for the CSS (don't place CSS under
    additional_links to improve clarity and template inheritance)
    *  **additional_js**    : All JS that need to be loaded in the head
    section
    
    *  </head>
    *  <body>
    
    *  **header** : Here is the header include. By default, the header is
    in English. (file: ``django_epfl/template_inc/header.en.html``) To
    see the other options, take a look the 
    :ref:`change header language part <change_language>`.
    *  <div id="main content">
    
    *  **breadcrumbs** : It is where you will put the "EPFL > Project >
    Section" navigation style.
    *  **languages** : Links in the top right corner that permit the
    user to switch between languages. 
    *  <h1>
    
    *  **title** : Area for the title of the project and (in general)
    its acronym.
    
    *  </h1>
    *  **main-navigation** : Area that contains droplists and all the 
    navigation for the project.
    *  **tools** : Space for the tools like RSS feed button, share 
    button and so on.
    *  <div id="content">
    
    *  **content** : Contains the main content for the page.
    
    *  </div>
    *  <div id="right-col">
    
    *  **right_column** : Contains the secondary content in the right
    column. If empty, the template will automatically switch to
    1-column mode and the "right-col" div will not be displayed.
    
    *  </div>
    *  **footer** : Area for general contents like contact link, 
    copyright, ...
    
    *  </div>
    
    *  **additional_js_ajax** : Place JS that don't need to be loaded 
    first.
    
    *  </body>
    
    *  </html>
    
    List of available variables
    ===========================
    
    For the moment, only the ``title`` var (representing the page title) is 
    available. Care to not be confused with the ``title`` block which is the big 
    black title on the page.
    
    Use the EPFL error pages
    ========================
    
    In order to handle EPFL 404 error page, you have to modify your file 
    ``views.py`` and put in it this::
    
    from django.shortcuts import render_to_response
    
    def error404(request):
    return render_to_response('django_epfl/errors/404.fr.html')
    
    Then, in your ``urls.py``::
    
    from django.conf.urls.defaults import handler404
    
    handler404 = 'django_site.views.error404'
    
    To handle the 500 error, it is the same logic. Since errors like
    503 are not natively supported, you will have to create and raise it in your 
    code. Some explanations on how to do this 
    `here <http://mitchfournier.com/2010/07/12/show-a-custom-403-forbidden-error-page-in-django/>`_.
    
    https://docs.djangoproject.com/en/1.3/ref/request-response/#ref-httpresponse-subclasses
    can help you too if you need to return some HttpResponse with a defined status
    code.
    
    .. note::
    The 404 and 500 error pages won't be displayed if ``DEBUG`` is set to 
    ``True``.
    
    .. _change_language:
    
    Change header language / search option
    ======================================
    
    You can change the header with the **header** block.
    
    There are four different headers available in the ``templates/template_inc`` dir:
    * header.fr.html 
    * header.en.html
    * header-no-local-search.fr.html
    * header-no-local-search.en.html
    
    Obviously, in the header name, *fr* means French and *en* English. The 
    *no-local-search* version of the header does not include the search option "On
    this site".
    """

setup(
      name='django_epfl',
      version=version,
      description="django_epfl",
      long_description=LONG_DESCRIPTION,
      classifiers=[
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Framework :: Django",
                   "Environment :: Web Environment",
                   ],
      keywords='epfl,template,django_epfl,tequila,django-tequila,django-pagination,django',
      author='Romain Gehrig',
      author_email='romain.gehrig@epfl.ch',
      url='http://kis-doc.epfl.ch/django',
      license='GNU GPLv3',
      packages=find_packages(),
      include_package_data= True,
      requires=['setuptools'],
      zip_safe= False,
      )
