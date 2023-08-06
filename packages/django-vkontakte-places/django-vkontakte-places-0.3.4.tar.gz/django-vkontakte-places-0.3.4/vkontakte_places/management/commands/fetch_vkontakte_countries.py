# -*- coding: utf-8 -*-
from django.core.management.base import AppCommand
from vkontakte_places.models import Country

class Command(AppCommand):
    help = 'Fetch all countries from vkontakte via API'
    requires_model_validation = True

    def handle(self, **options):
        countries = Country.remote.fetch(need_full=1)
        return u'Saved successfuly %d countries\n' % len(countries)