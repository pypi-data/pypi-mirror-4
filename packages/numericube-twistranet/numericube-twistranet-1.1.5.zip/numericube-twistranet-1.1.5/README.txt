
This is the twistranet project!

(c)2011 NumeriCube (http://www.numericube.com)

Official website: http://www.twistranet.com / French version on http://www.twistranet.fr

About
=====

twistranet is an Enterprise Social Software.
It's a Social Network you can use to help people collaborate.
And it is also a nice CMS (Content Management System) with a social focus.

twistranet is published under the termes of the GNU Affero General Public License v3.

Requirements
============

TwistraNet is written in PYTHON (>= 2.6, or >= 2.5 + simplejson)
Twistranet is based on Django Framework (as of writing, Django >= 1.2 is mandatory,
Django >= 1.3 is highly recommanded).

If Django is always installed you can install twistranet over your Django platform.
Otherwise The last Django version will be downloaded and installed at setup.

Other requirements:

- python-setuptools

- python-imaging (aka PIL)

- python-ldap, only if you want to authenticated against LDAP/Active Directory.

Installation
============

Installation - short version
-----------------------------

- Install requirements (Python, SetupTools and PIL)

- Download and untar (or unzip) twistranet from https://github.com/numericube/twistranet/tarball/master

- In the unzipped directory, just execute:

  - (sudo) python ./setup.py install clean

twistranet is now installed. You can have many sites with just one twistranet installation, so you need to explicitly deploy and bootstrap your new site.

  - (sudo) twistranet_project <path_to_my_new_site>

Don't forget to write down your generated admin password!!

Your server should now be fully working and running on http://localhost:8000 !

If you want to start it again:

- cd <path_to_my_new_site>

- python ./manage.py runserver 0.0.0.0:8000

Installation - the Big Picture
------------------------------

Installation is in fact a 2 steps process. You must install twistranet's core features as a python library,
then you have to create a project (which is an instance of a twistranet site).

To install twistranet's core features:

- Download and install Python >= 2.6 (with setuptools and PIL)

- Execute (as a superuser) "easy_install numericube-twistranet" ; this will normally download and install twistranet and all dependencies.

To create a new project:

- In the directory you want your website files created, type "python twistranet_project -n [<template>] <project_path>",
    where <project_path> is the name of your site (it will be created by the process) ;
    <template> is the name of the project template to deploy. Currently admitted values are:
        
    - 'default' (which is... the default value), an empty project based on sqlite;
    
    - 'cogip', a sample french-language project of a fictious company called COGIP.
    
The '-n' (or '--no-bootstrap') is an option to tell the twistranet_project script not to bootstrap it
immediately (the bootstraping process is the initial database feed).

You can do it by hand once (and only once!) with the following commands:

- Go to your <project_path>

- Review the settings.py file and local_settings.py, change to whatever suits your needs.

  Among other things, carefully choose your DATABASE scheme, your LDAP/AD settings and the 'admin' password
  that has been generated for you.

- Execute "./manage.py bootstrap" to build the database

Running Twistranet :

- Execute ./manage.py runserver 0.0.0.0 to start playing with twistranet.

- Point your browser at http://localhost:8000


More informations
=================

You can get other informations in the "docs" folder inside this package about:

- installing/upgrading/uninstalling twistranet with PIP (quick and clean)

- installing Twistranet for testing and development
  (using virtualenv / installing in place the devel package / localization / running tests ...)

- Running Twistranet in debug mode


Troubleshooting
================

No image / thumbnail on my fresh twistranet instance!
------------------------------------------------------

This is probably a problem with python-imaging installation. Just install PIL for your OS.

Under debian, the easiest is to do "apt-get install python-imaging".

error: Could not find required distribution Django
---------------------------------------------------

If you've got this message, that means the autoinstall procedure of twistranet can't install django automatically.
Just install django (see www.django-project.org) either from sources or from a package from your OS,
and run "python setup.py install" again.

Seems that it is a python-2.5 related problem.

I've lost my admin password!
----------------------------

It's easy to set a new one.

- Stop your server

- Run ./manage.py changepassword admin (and change your password)

- Start your server again

error when using mod_python
---------------------------
mod_wsgi is recommended, but if you need mod_python
this little django1.2.5 hack is needed :

- in django.http.init: do not use "from mod_python.util import parse_qsl"

replace the lines 7 to 11 with::

  from cgi import parse_qsl

Thanks to esimorre https://github.com/numericube/twistranet/issues#issue/6


Greetings
==========

Email templates are inspired from MailChimp's Email-Blueprints (https://github.com/mailchimp/Email-Blueprints). We do love Mailchimp and strongly recommand it if you want a powerful mailing-list solution!

MimeTypes Icons came from Farm Fresh Free icons Collection, under Creative Commons 3.0 License. Many thanks to http://www.fatcow.com/free-icons