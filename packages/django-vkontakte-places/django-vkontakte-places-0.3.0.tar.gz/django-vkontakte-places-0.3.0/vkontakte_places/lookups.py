from ajax_select import LookupChannel
from models import City, Country

class VkontakteLookupChannel(LookupChannel):

    def get_pk(self,obj):
        return getattr(obj,'remote_id')

    def get_objects(self, ids):
        ids = [int(id) for id in ids]
        return self.model.objects.filter(remote_id__in=ids)

class CityLookup(VkontakteLookupChannel):
    model = City
    search_field = 'name'

    def get_query(self, q, request):
        # TODO: make somehow available all countries
        return self.model.remote.fetch(country=1, q=q)

class CountryLookup(VkontakteLookupChannel):
    model = Country
    search_field = 'name'