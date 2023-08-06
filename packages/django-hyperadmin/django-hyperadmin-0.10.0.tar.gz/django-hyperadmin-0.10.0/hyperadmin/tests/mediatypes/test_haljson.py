from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from hyperadmin.mediatypes.haljson import HalJSON
from hyperadmin.resources.directory import ResourceDirectory
from hyperadmin.sites import site

from common import MediaTypeTestCase

class HalJsonTestCase(MediaTypeTestCase):
    content_type = 'application/hal+json'
    
    def get_adaptor(self):
        self.api_request = self.get_api_request()
        return HalJSON(self.api_request)
    
    def test_queryset_serialize(self):
        endpoint = self.resource.endpoints['list'].fork(api_request=self.api_request)
        
        link = endpoint.link_prototypes['list'].get_link()
        state = endpoint.state
        
        response = self.adaptor.serialize(content_type=self.content_type, link=link, state=state)
        data = json.loads(response.content)
        json_items = data['collection']['items']
        self.assertEqual(len(json_items), len(ContentType.objects.all()))
    
    def test_model_instance_serialize(self):
        instance = ContentType.objects.all()[0]
        endpoint = self.resource.endpoints['detail'].fork(api_request=self.api_request)
        
        endpoint.state.item = item = endpoint.get_resource_item(instance)
        link = item.get_link()
        state = endpoint.state
        
        response = self.adaptor.serialize(content_type=self.content_type, link=link, state=state)
        data = json.loads(response.content)
        json_items = data['collection']['items']
        self.assertEqual(len(json_items), 1)
    
    def test_directory_resource_serialize(self):
        site_resource = site.directory_resource
        
        def get_prompt(*args):
            return _('lazy string')
        
        endpoint = site_resource.endpoints['list'].fork(api_request=self.api_request)
        
        link = endpoint.link_prototypes['list'].get_link()
        state = endpoint.state
        state.resource.get_prompt = get_prompt
        
        response = self.adaptor.serialize(content_type=self.content_type, link=link, state=state)
        data = json.loads(response.content)
        json_items = data['collection']['items']
        self.assertEqual(data['collection']['prompt'], 'lazy string')
    
    def test_model_instance_deserialize(self):
        pass
        #items = [ContentType.objects.all()[0]]
        #payload = '''{"data":{}}'''
        #return
        #view.request = view.factory.post('/', **{'wsgi.input':FakePayload(payload), 'CONTENT_LENGTH':len(payload)})
        #adaptor = CollectionJSON(view)
        #data = adaptor.deserialize()
        #json_items = data['collection']['items']
