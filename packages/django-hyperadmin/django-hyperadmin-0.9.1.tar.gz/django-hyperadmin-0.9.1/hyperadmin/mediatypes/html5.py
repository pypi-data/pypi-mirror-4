from django.template.response import TemplateResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings

from hyperadmin.mediatypes.common import MediaType


class Html5MediaType(MediaType):
    template_name = 'hyperadmin/html5/resource.html'
    template_dir_name = 'hyperadmin/html5'
    response_class = TemplateResponse
    recognized_media_types = [
        'text/html',
        'text/plain',
        'application/xhtml+xml',
        'application/text-html',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
    ]
    
    def get_context_data(self, link, state):
        context = {'link':link,
                   'meta':state.meta,
                   'state':state,}
        
        context['namespaces'] = state.get_namespaces()
        
        if 'display_fields' in state.meta:
            context['display_fields'] = state.meta['display_fields']
        
        view_class_context = 'get_%s_context_data' % state['endpoint_class']
        if hasattr(self, view_class_context):
            context = getattr(self, view_class_context)(link, state, context)
        
        #strangely for django 1.3
        if 'STATIC_URL' not in context and getattr(settings, 'STATIC_URL', None):
            context['STATIC_URL'] = getattr(settings, 'STATIC_URL')
        
        if hasattr(state['endpoint'], 'get_context_data'):
            context = state['endpoint'].get_context_data(**context)
        
        return context
    
    def get_template_names(self, state):
        if hasattr(state['endpoint'], 'get_template_names'):
            names = state['endpoint'].get_template_names()
            if names: return names
        
        params = {
            'base': self.template_dir_name,
            'endpoint_class': state['endpoint_class'],
            'resource_name': state.get('resource_name', None),
            'app_name': state.get('app_name', None),
        }
        
        names = [
            '{base}/{app_name}/{resource_name}/{endpoint_class}.html'.format(**params),
            '{base}/{app_name}/{endpoint_class}.html'.format(**params),
            '{base}/{endpoint_class}.html'.format(**params),
            self.template_name,
        ]
        
        return names
    
    def serialize(self, content_type, link, state):
        if self.detect_redirect(link):
            return self.handle_redirect(link)
        context = self.get_context_data(link=link, state=state)
        
        response = self.response_class(request=self.get_django_request(), template=self.get_template_names(state), context=context)
        response['Content-Type'] = 'text/html'
        
        return response
    
    def get_option_template_names(self):
        return ['{base}/options.html'.format(base=self.template_dir_name)]
    
    def options_serialize(self, content_type, links, state):
        context = {
            'links':links,
            'content_type':content_type,
            'allow':','.join(links.iterkeys()),
        }
        response = self.response_class(request=self.get_django_request(), template=self.get_option_template_names(), context=context)
        response['Allow'] = context['allow']
        return response
    
    def deserialize(self):
        request = self.get_django_request()
        self.check_csrf(request)
        
        return {'data':request.POST,
                'files':request.FILES,}
    
    def check_csrf(self, request):
        csrf_middleware = CsrfViewMiddleware()
        response = csrf_middleware.process_view(request, self.deserialize, [], {})
        if response is not None:
            assert False, 'csrf failed' #TODO APIException(response) or SuspiciousOperation ....
            raise response

Html5MediaType.register_with_builtins()

