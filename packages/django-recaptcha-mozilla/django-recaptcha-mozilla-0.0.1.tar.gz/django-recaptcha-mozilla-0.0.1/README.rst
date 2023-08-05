Mozilla fork of:

http://github.com/praekelt/django-recaptcha

Originally written by the Praekelt Foundation.

Inspired by
===========
Marco Fucci @ http://www.marcofucci.com/tumblelog/26/jul/2009/integrating-recaptcha-with-django/


Requirements
===========
This version requires a custom version of the python-recaptcha library to provide ssl support for submit.
You can get the required version here:

http://github.com/bltravis/python-recaptcha

Add a new setting to your Django project settings file (eg.):

RECAPTCHA_USE_SSL = True

If you don't add this setting, the code is written to default to **NOT** use SSL.
