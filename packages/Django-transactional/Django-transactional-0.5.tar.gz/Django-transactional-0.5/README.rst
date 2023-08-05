====================
Django Transactional
====================

Easy package to add simple transactional ModelForm forms in your django app.
Uses url to build transaction for you translating **/APP/MODEL/add/** into:

- app: APP
- model: model MODEL from app APP
- form: ModelForm form from app APP
- template: APP_MODEL.html

And will present the user with the template to file it and submit, once submited it will return a json with {'success': True} or with {'sucess': False, 'errors': ERRORS}

Usage
=====

urls.py
-------
Add django transactional to your urls.py. It will accept urls of the form: **/APP/MODEL/add/** to add new model objects and **/APP/MODEL/add/OBJECT_ID/** to edit data in model object with id *OBJECT_ID*::

    url(r'^', include('dtrans.urls')),

Templates
---------
The templates must be named *APP_MODEL*.html in lower case letters and it will get **obj_form** as a parameter that can be used in the template code.

Forms
-----
Forms should be named *ModelForm* where *Model* is capitalized. If it's not present it will create a basic ModelForm:

::

    class ObjectForm(ModelForm):
        class Meta:
            model = MODEL

Settings
--------
Add *dtrans* to your installed apps.

::

    DTRANS_CONF = {
        'force_urls': False,                   # Force urls nicknames
        'apps_urls': {nickname: app name},     # Dictionary with nick to app key values
        'models_urls': {nickname: model name}, # Dictionary with nick to model key values
        'template_suffix': 'suffix',           # suffix to add at the end of template names
    }

Examples
========

foo/models.py
-------------
::

    class Bar(models.Model):
        name = models.CharField(max_length=10)

foo/forms.py
------------
::

    class BarForm(models.ModelForm):
        class Meta:
            model = Bar

foo_bar.html
------------
::

    <form action=".">
      {{ obj_form.as_p }}
      <input type="submit" value="Submit">
    </form>
