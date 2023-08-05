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


class Request(object):
    def __init__(self, request, app_url, model_url, obj_id):
        self.app_name, self.module_name = self._url_to_name(app_url, 'app')
        self.model_name = self._url_to_name(model_url, 'model')[0]

        self.cap_model = self.model_name.capitalize()
        self.form_name = '%sForm' % self.cap_model

        self.request = request

        self.obj_id = obj_id

    @property
    def conf(self):
        if hasattr(settings, 'DTRANS_CONF'):
            return settings.DTRANS_CONF
        else:
            raise ImproperlyConfigured(
                'You must define DTRANS_CONF in your settngs.py'
            )

    @property
    def models(self):
        """
        Gets APP models module.

        """
        try:
            return get_app(self.app_name)
        except ImproperlyConfigured:
            raise Http404

    @property
    def cls(self):
        """
        Gets model class.

        """
        if hasattr(self.models, self.cap_model):
            return getattr(self.models, self.cap_model)
        else:
            raise Http404

    @property
    def form_obj(self):
        """
        Gets form.

        """
        try:
            exec 'from %s.forms import %s' % (self.app_name, self.form_name)
        except ImportError:
            from django.forms import ModelForm
            meta = type('Meta', (), {"model": self.cls})
            mf_class = type('modelform', (ModelForm,), {"Meta": meta})
        else:
            mf_class = eval(self.form_name)

        return mf_class

    @property
    def template(self):
        """
        Gets template name.

        """
        template_name = '%s_%s%s.html' % (
            self.app_name, self.model_name,
            self.conf.get('template_sufix', '')
        )

        try:
            loader.get_template(template_name)
        except TemplateDoesNotExist:
            template_name = 'dtrans_default_form.html'

        return template_name

    def _url_to_name(self, url, kind):
        """
        Get app or model name from url.
        Translates from dtrans config if present.

        """
        name = url
        module = url

        conf_key = "%ss_urls" % kind

        if (conf_key in self.conf) and (url in self.conf[conf_key]):
            name = self.conf[conf_key][url].split('.')[-1]
            module = self.conf[conf_key][url]

        return name, module


    def process_request(self):
        """
        Process Request

        Key arguments:
            - request: request object.
            - cls: class to add to or modify.
            - form_obj: object's ModelForm
            - obj_id: object it to modify.

        """
        success = False
        if self.request.method == 'POST':
            post = self.request.POST

            if self.obj_id:
                obj = get_object_or_404(self.cls, pk=self.obj_id)
                form = self.form_obj(post, instance=obj)
            else:
                form = self.form_obj(post)

            if form.is_valid():
                obj = form.save()
                success = True

            ans_type = self.conf.get('answer', 'html')

            if ans_type == 'json':
                if success:
                    res = {
                        'success': True,
                        'id': obj.id,
                        'unicode': unicode(obj)
                    }
                else:
                    res = {'success': False, 'errors': form.errors}

                json = simplejson.dumps(res)
                return HttpResponse(json, mimetype='application/json')
            elif not ans_type == 'html':
                msg = (
                    'Unrecognized answer type: %s.'
                    ' Options are \'json\' or \'html\''
                ) % ans_type
                raise ImproperlyConfigured(msg)
        else:
            if self.obj_id:
                obj = self.cls.objects.get(id=self.obj_id)
                form = self.form_obj(instance=obj)
            else:
                form = self.form_obj()

        data = {
            'form_name': self.form_name,
            'obj_form': form,
            'success': success
        }

        return render_to_response(
            self.template, data,
            context_instance=RequestContext(self.request)
        )


def add_or_modify(request, app_url, model_url, obj_id=None):
    """
    Add or Modify. Imports needed modules and calls the request processing
    method.

    Key arguments:
        app_name: Django app to import stuff from.
        model_name: app model to use.
        obj_id: object to modify.

    """
    req = Request(request, app_url, model_url, obj_id)
    return req.process_request()
