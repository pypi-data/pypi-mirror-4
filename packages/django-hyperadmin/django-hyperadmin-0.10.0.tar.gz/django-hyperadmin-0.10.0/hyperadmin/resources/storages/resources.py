import os

from django.core.exceptions import ObjectDoesNotExist

from hyperadmin.links import Link
from hyperadmin.resources.crud import CRUDResource
from hyperadmin.resources.storages.forms import UploadForm, Base64UploadForm, UploadLinkForm
from hyperadmin.resources.storages.indexes import StorageIndex
from hyperadmin.resources.storages.endpoints import ListEndpoint, CreateUploadEndpoint, Base64UploadEndpoint, BoundFile


class StorageQuery(object):
    def __init__(self, storage, path=''):
        self.storage = storage
        self.path = path

    def filter(self, path):
        if self.path:
            path = os.path.join(self.path, path)
        return StorageQuery(self.storage, path)

    def get_dirs_and_files(self):
        try:
            dirs, files = self.storage.listdir(self.path)
        except NotImplementedError:
            return [], []
        if self.path:
            files = [os.path.join(self.path, filename) for filename in files]
        return dirs, [BoundFile(self.storage, filename) for filename in files]

    def get(self, path):
        if self.path:
            path = os.path.join(self.path, path)
        if not self.storage.exists(path):
            raise ObjectDoesNotExist
        return BoundFile(self.storage, path)


class StorageResource(CRUDResource):
    #resource_adaptor = storage object
    form_class = UploadForm
    upload_link_form_class = UploadLinkForm
    base64_upload_form_class = Base64UploadForm
    list_endpoint = (ListEndpoint, {})
    create_upload_endpoint = (CreateUploadEndpoint, {})
    base64_upload_endpoint = (Base64UploadEndpoint, {})

    def __init__(self, **kwargs):
        kwargs.setdefault('app_name', '-storages')
        super(StorageResource, self).__init__(**kwargs)

    def get_storage(self):
        return self.resource_adaptor
    storage = property(get_storage)

    def get_base64_upload_form_class(self):
        return self.base64_upload_form_class

    def get_upload_link_form_class(self):
        return self.upload_link_form_class

    def get_view_endpoints(self):
        endpoints = super(StorageResource, self).get_view_endpoints()
        endpoints.insert(0, self.create_upload_endpoint)
        return endpoints

    def get_indexes(self):
        return {'primary': StorageIndex('primary', self)}

    def get_primary_query(self):
        return StorageQuery(self.storage)

    def get_instances(self):
        '''
        Returns a set of native objects for a given state
        '''
        if 'page' in self.state:
            return self.state['page'].object_list
        if self.state.has_view_class('change_form'):
            return []
        dirs, files = self.get_primary_query()
        instances = [BoundFile(self.storage, file_name) for file_name in files]
        return instances

    def get_item_form_kwargs(self, item=None, **kwargs):
        kwargs = super(StorageResource, self).get_item_form_kwargs(item, **kwargs)
        kwargs['storage'] = self.storage
        return kwargs

    def get_form_kwargs(self, **kwargs):
        kwargs = super(StorageResource, self).get_form_kwargs(**kwargs)
        kwargs['storage'] = self.storage
        return kwargs

    def get_upload_link_form_kwargs(self, **kwargs):
        kwargs = self.get_form_kwargs(**kwargs)
        kwargs['resource'] = self
        kwargs['request'] = self.api_request.request
        return kwargs

    def get_item_url(self, item):
        return self.link_prototypes['update'].get_url(item=item)

    def get_item_storage_link(self, item, **kwargs):
        link_kwargs = {'url': item.instance.url,
                       'resource': self,
                       'prompt': 'Absolute Url',
                       'rel': 'storage-url', }
        link_kwargs.update(kwargs)
        storage_link = Link(**link_kwargs)
        return storage_link

    def get_item_outbound_links(self, item):
        links = self.create_link_collection()
        links.append(self.get_item_storage_link(item, link_factor='LO'))
        return links

    def get_item_prompt(self, item):
        return item.instance.name

    def get_paginator_kwargs(self):
        return {}
