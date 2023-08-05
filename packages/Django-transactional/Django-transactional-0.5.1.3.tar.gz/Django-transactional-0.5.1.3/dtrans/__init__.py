# -*- coding: UTF-8 -*-
"""
Utils lib.

Copyright (C) 2012 Corp B2C S.A.C.

Authors:
    Nicolas Valcarcel Scerpella <nvalcarcel@corpb2c.com>

"""
# std imports

# 3rd party imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, TemplateDoesNotExist, loader
from django.utils import simplejson

# internal imports


def add_or_modify(request, app_url, model_url, obj_id=None):
    """
    Add or Modify. Imports needed modules and calls the request processing
    method.

    Key arguments:
        app_name: Django app to import stuff from.
        model_name: app model to use.
        obj_id: object to modify.

    """
    app_name, module_name = url_to_name(app_url, 'app')
    model_name = url_to_name(model_url, 'model')[0]

    cap_model = model_name.capitalize()
    form_name = '%sForm' % cap_model
    template_name = get_template(app_name, model_name)

    models = get_models(app_name)
    cls = get_class(models, cap_model)
    form_obj = get_form(module_name, form_name, cls)

    return process_request(
        request, cls, form_obj, form_name, obj_id, template_name)


def get_models(app_name):
    """
    Gets APP models module.

    """
    try:
        models = get_app(app_name)
    except ImproperlyConfigured:
        raise Http404

    return models


def get_class(app, model_name):
    """
    Gets model class.

    """
    if hasattr(app, model_name):
        return getattr(app, model_name)
    else:
        raise Http404


def get_form(app_name, form_name, cls):
    """
    Gets form.

    """
    try:
        exec 'from %s.forms import %s' % (app_name, form_name)
    except ImportError:
        from django.forms import ModelForm
        meta = type('Meta', (), { "model": cls, })
        mf_class = type('modelform', (ModelForm,), {"Meta": meta})
    else:
        mf_class = eval(form_name)

    return mf_class


def get_template(app_name, model_name):
    """
    Gets template name.

    """
    template_name = '%s_%s.html' % (app_name, model_name)

    if hasattr(settings, 'DTRANS_CONF'):
        conf = settings.DTRANS_CONF

        if 'template_sufix' in conf:
            template_name = '%s_%s_%s.html' % (
                app_name, model_name, conf['template_sufix'])

    try:
        loader.get_template(template_name)
    except TemplateDoesNotExist:
        template_name = 'dtrans_default_form.html'

    return template_name


def url_to_name(url, kind):
    """
    Get app or model name from url. Translates from dtrans config if present.

    """
    name = url
    module = url

    if hasattr(settings, 'DTRANS_CONF'):
        conf = settings.DTRANS_CONF
        conf_key = "%ss_urls" % kind

        if (conf_key in conf) and (url in conf[conf_key]):
            name = conf[conf_key][url].split('.')[-1]
            module = conf[conf_key][url]

    return name, module


def process_request(request, cls, form_obj, form_name, obj_id, template):
    """
    Process Request

    Key arguments:
        - request: request object.
        - cls: class to add to or modify.
        - form_obj: object's ModelForm
        - obj_id: object it to modify.

    """
    if obj_id:
        obj = cls.objects.get(id=obj_id)
        form = form_obj(instance=obj)
    else:
        form = form_obj()

    if request.method == 'POST':
        post = request.POST
        success = False
        res = {}

        if obj_id:
            obj = get_object_or_404(cls, pk=obj_id)
            form = form_obj(post, instance=obj)
        else:
            form = form_obj(post)

        if form.is_valid():
            form.save()
            success = True

            json = simplejson.dumps(res)
            return HttpResponse(json, mimetype='application/json')

    data = {
        'form_name': form_name,
        'obj_form': form
    }

    return render_to_response(
        template, data, context_instance=RequestContext(request))
