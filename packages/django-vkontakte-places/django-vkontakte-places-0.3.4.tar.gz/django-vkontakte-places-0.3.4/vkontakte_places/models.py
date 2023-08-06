# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import FieldDoesNotExist
from django.core.exceptions import ValidationError
from datetime import datetime, date
from vkontakte_api.utils import api_call
from vkontakte_api import fields
from vkontakte_api.models import VkontakteManager, VkontakteIDModel
import logging
import time

log = logging.getLogger('vkontakte_places')

class PlacesManager(VkontakteManager):

    def api_call(self, *args, **kwargs):

        if 'ids' in kwargs and 'get_by_ids' in self.methods:
            kwargs['cids'] = ','.join(map(lambda i: str(i), kwargs.pop('ids')))
            method = self.methods['get_by_ids']
        else:
            if 'country' in kwargs and isinstance(kwargs['country'], Country):
                kwargs['country'] = kwargs['country'].remote_id
            method = self.methods['get']
        return api_call(self.model.methods_namespace + '.' + method, **kwargs)

    def get(self, *args, **kwargs):
        '''
        Apply country param request to all instances in reponse
        '''
        country = None

        if 'country' in kwargs and self.model._meta.get_field('country'):
            if isinstance(kwargs['country'], Country):
                country = kwargs['country']
            else:
                country = Country.objects.get(remote_id=kwargs['country'])

        instances = super(PlacesManager, self).get(*args, **kwargs)

        if country:
            for instance in instances:
                instance.country = country

        return instances

class PlacesModel(VkontakteIDModel):
    class Meta:
        abstract = True

    methods_namespace = 'places'

    def parse(self, response):
        super(PlacesModel, self).parse(response)

        # this field becouse in different queries different name of field in response:
        # http://vk.com/developers.php?oid=-1&p=places.getCities
        # http://vk.com/developers.php?oid=-1&p=places.getCityById
        if 'title' in response and not self.name:
            self.name = response['title']

class Country(PlacesModel):
    class Meta:
        verbose_name = u'Страна Вконтакте'
        verbose_name_plural = u'Страны Вконтакте'
        ordering = ['name']

    remote_pk_field = 'cid'

    name = models.CharField(max_length=50)

    remote = PlacesManager(remote_pk=('remote_id',), methods={
        'get': 'getCountries',
        'get_by_ids': 'getCountryById',
    })

    def __unicode__(self):
        return self.name

class City(PlacesModel):
    class Meta:
        verbose_name = u'Город Вконтакте'
        verbose_name_plural = u'Города Вконтакте'
        ordering = ['name']

    remote_pk_field = 'cid'

    country = models.ForeignKey(Country, null=True, related_name='cities', help_text=u'Страна')
    name = models.CharField(max_length=50)

    # not exist in API docs
    area = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    remote = PlacesManager(remote_pk=('remote_id',), methods={
        'get': 'getCities',
        'get_by_ids': 'getCityById',
    })

    def __unicode__(self):
        name = [self.name]
        if self.region:
            name += [self.region]
        if self.area:
            name += [self.area]
        return ', '.join(name)

class Region(PlacesModel):
    class Meta:
        verbose_name = u'Регион Вконтакте'
        verbose_name_plural = u'Регионы Вконтакте'
        ordering = ['name']

    remote_pk_field = 'region_id'

    country = models.ForeignKey(Country, related_name='regions', help_text=u'Страна')
    name = models.CharField(max_length=50)

    remote = PlacesManager(remote_pk=('remote_id',), methods={
        'get': 'getRegions',
    })

    def __unicode__(self):
        return self.name