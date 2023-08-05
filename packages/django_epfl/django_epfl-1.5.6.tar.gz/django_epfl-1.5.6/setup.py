from setuptools import setup, find_packages

version = '1.5.6'

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
      name='django_epfl',
      version=version,
      description="Django utils for EPFL sites",
      long_description=README_TEXT,
      classifiers=[
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Framework :: Django",
                   "Environment :: Web Environment",
                   ],
      keywords='epfl,templates,django_epfl,tequila,django-tequila,django-pagination,django',
      author='Romain Gehrig',
      author_email='romain.gehrig@epfl.ch',
      url='http://kis-doc.epfl.ch/django',
      license='GNU LGPLv3',
      packages=find_packages(),
      include_package_data= True,
      requires=['setuptools'],
      data_files=[('readme', ['README.rst'])],
      zip_safe= False,
      )
