import os
from setuptools import setup, find_packages
from twistranet import VERSION, __version__

setup(name = 'numericube-twistranet',
      version = __version__,
      description = "twistranet - An Enterprise Social Network",
      long_description =open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: "
                                            "Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",        
        "License :: OSI Approved :: GNU Affero General Public License v3",
        ],
      keywords = 'twistranet Enterprise Social Network',
      author = 'numeriCube',
      author_email = 'twistranet@numericube.com',
      url = 'http://numericube.com',
      license = 'GNU Affero General Public License v3',
      packages = ['twistranet'], #find_packages(exclude=['ez_setup']),
      include_package_data = True,
      zip_safe = False,
      dependency_links = ['http://django-modeltranslation.googlecode.com/files/django-modeltranslation-0.2.tar.gz',],
      install_requires = [
          'Django<=1.3.3',
          'django-debug-toolbar==0.8.4',
          'django-piston==0.2.2',
          'django-haystack==1.1.0',
          'django-tinymce==1.5.1a1',
          'django-modeltranslation==0.2',
          'sorl-thumbnail==11.01',
          # -*- Extra requirements: -*-
      ],
      entry_points = """
      # -*- Entry points: -*-
      [console_scripts]
      twistranet_project=twistranet.core.twistranet_project:twistranet_project
      """,
      )
