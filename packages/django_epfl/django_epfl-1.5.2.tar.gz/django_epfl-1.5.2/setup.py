from setuptools import setup, find_packages

version = '1.5.2'

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
      name='django_epfl',
      version=version,
      description="django_epfl",
      long_description=README_TEXT,
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
