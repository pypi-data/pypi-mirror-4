# -*- coding: UTF-8 -*-
"""
Setup file.

Copyright (C) 2012 Corp B2C S.A.C.

Authors:
    Nicolas Valcarcel Scerpella <nvalcarcel@corpb2c.com>

"""

from distutils.core import setup
setup(
    name='Django-transactional',
    version='0.5.1',
    description='Python module for doing common transactions in Django.',
    author='Nicolas Valcarcel Scerpella',
    author_email='nvalcarcel@corpb2c.com',
    url='http://code.corpb2c.com/django-transactional',
    packages=['dtrans'],
    package_data={'dtrans': ['templates/*.html']},
    license='BSD',
    long_description="""
Easy package to add simple transactional ModelForm forms in your django app.
Uses url to build transaction for you translating /APP/MODEL/add/ into:
  * app: APP
  * model: model MODEL from app APP
  * form: ModelForm form from app APP
  * template: APP_MODEL.html

And will present the user with the template to file it and submit, once
submited it will return a json with {'success': True} or with
{'sucess': False, 'errors': ERRORS}""",
)
