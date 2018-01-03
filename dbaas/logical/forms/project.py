# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
from django.forms import models
from django.db.models.fields import FieldDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django import forms
from ..models import Project


class RemoteChoiceField(forms.ChoiceField):
    """
        Field for get choices from any API

        required params:
            - remote_host: api host
            - remote_url: url of api
            - model_instance: model instance
            - name: name of field on model
    """

    remote_url = None
    remote_host = None
    model_instance = None

    def __init__(self, *args, **kw):
        self.validate_params(kw)
        self.model_instance = kw.pop('model_instance')
        self.remote_url = kw.pop('remote_url')
        self.remote_host = kw.pop('remote_host')
        self.name = kw.pop('name')
        kw.update({
            'choices': self.get_choices()
        })

        super(RemoteChoiceField, self).__init__(*args, **kw)

        self.update_choices_on_instance()

    def validate_params(self, params):
        for k in ('model_instance', 'remote_host', 'remote_url', 'name'):
            if k not in params:
                raise ImproperlyConfigured('This param <{}> is required'.format(k))

    def get_choices(self):
        empty_choice = [('', '')]
        if self.remote_host and self.remote_url:
            resp = requests.get('{}{}'.format(
                self.remote_host, self.remote_url)
            )
            if resp.ok:
                remote_choices = map(
                    lambda i: (str(i['id_service_now']), i['nome']),
                    sorted(resp.json(), key=lambda i: i['nome'])
                )
                return empty_choice + remote_choices
        return empty_choice

    def update_choices_on_instance(self):
        try:
            field = self.model_instance._meta.get_field_by_name(self.name)[0]
        except (FieldDoesNotExist, IndexError):
            pass
        else:
            field._choices = self.choices


class ProjectForm(models.ModelForm):

    class Meta:
        model = Project
        widgets = {
            'slug': forms.HiddenInput(),
        }

    def __init__(self, *args, **kw):
        super(ProjectForm, self).__init__(*args, **kw)
        self.fields['business_service'] = RemoteChoiceField(
            required=True, label='Business Service',
            remote_host='http://dicionario.dev.globoi.com',
            remote_url='/v1/custeio/servicos-de-negocio',
            model_instance=self.instance,
            name='business_service'
        )
        self.fields['client'] = RemoteChoiceField(
            required=True, label='Client',
            remote_host='http://dicionario.dev.globoi.com',
            remote_url='/v1/custeio/clientes',
            model_instance=self.instance,
            name='client'
        )
        self.fields['product'] = RemoteChoiceField(
            required=True, label='Product',
            remote_host='http://dicionario.dev.globoi.com',
            remote_url='/v1/custeio/produtos',
            model_instance=self.instance,
            name='product'
        )
        self.fields['component'] = RemoteChoiceField(
            required=True, label='Component',
            remote_host='http://dicionario.dev.globoi.com',
            remote_url='/v1/custeio/componentes',
            model_instance=self.instance,
            name='component'
        )
        self.fields['subcomponent'] = RemoteChoiceField(
            required=True, label='Subcomponent',
            remote_host='http://dicionario.dev.globoi.com',
            remote_url='/v1/custeio/sub-componentes',
            model_instance=self.instance,
            name='subcomponent'
        )
