# -*- coding: utf-8 -*-
from django.test import TestCase
from models import City, Country, Region
from factories import CityFactory, CountryFactory
import simplejson as json

class VkontaktePlacesTest(TestCase):

    def test_parse_city(self):

        response = '''
            {"response":[
                {"cid":1,"title":"Москва","region":"Regione Abruzzo область"},
                {"cid":1074996,"title":"Москва","area":"Порховский район","region":"Псковская область"},
                {"cid":1102561,"title":"Москва","area":"Пеновский район","region":"Тверская область"},
                {"cid":1130701,"title":"Москва","area":"Верхошижемский район","region":"Кировская область"}
            ]}
            '''
        country = CountryFactory.create(remote_id=1)
        instance = City(country=country)
        instance.parse(json.loads(response)['response'][0])
        instance.save()

        self.assertEqual(instance.remote_id, 1)
        self.assertEqual(instance.name, u'Москва')

        instance = City(country=country)
        instance.parse(json.loads(response)['response'][1])
        instance.save()

        self.assertEqual(instance.remote_id, 1074996)
        self.assertEqual(instance.name, u'Москва')
        self.assertEqual(instance.area, u"Порховский район")
        self.assertEqual(instance.region, u"Псковская область")

    def test_fetch_cities(self):

        self.assertEqual(City.objects.count(), 0)

        country = CountryFactory.create(remote_id=1)

        City.remote.fetch(country=country.remote_id)
        self.assertEqual(City.objects.count(), 18)
        self.assertEqual(City.objects.all()[0].country, country)

        City.remote.fetch(country=country)
        self.assertEqual(City.objects.count(), 18)

        City.objects.all().delete()
        City.remote.fetch(country=country, q=u'Москва')
        self.assertTrue(City.objects.count() > 1)

    def test_fetch_cities_by_id(self):

        self.assertEqual(City.objects.count(), 0)
        City.remote.fetch(ids=[1,2])
        self.assertEqual(City.objects.count(), 2)