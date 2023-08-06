import logging
from django.views.generic.detail import SingleObjectMixin
from django.template.loader import render_to_string
from jsonbase import JSONResponseMixin
from pgcontent.utils import get_object_by_ctype_id


log = logging.getLogger("pu.in.core")


class InlineActionMixin(JSONResponseMixin):

    """ Handle action in a JSON way.
    """

    handle_on_get = False
    handle_on_post = True    

    def handle_request(self, *args, **kwargs):

        """ Implement handle call to actually do something... Must
        return a tuple of (status, errors) """

        raise NotImplementedError

    def get(self, request, *args, **kwargs):

        if self.handle_on_get:
            kwargs['status'], kwargs['errors'] = self.handle_request()
        else:
            kwargs['status'] = 0
            kwargs['errors'] = ""

        return self.render_to_response(self.get_context_data(**kwargs));

    def post(self, request, *args, **kwargs):

        if self.handle_on_post:
            kwargs['status'], kwargs['errors'] = self.handle_request()
        else:
            kwargs['status'] = 0
            kwargs['errors'] = ""

        return self.render_to_response(self.get_context_data(**kwargs));


class InlineObjectActionMixin(InlineActionMixin, SingleObjectMixin):

    """ Action on object """

    def get_context_data(self, **kwargs):

        """ Base implementation that just returns the view's kwargs """

        context = super(InlineObjectActionMixin, 
                        self).get_context_data(**kwargs)

        context['object'] = self.object

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        return super(InlineObjectActionMixin, self).get(request, *args, 
                                                        **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        return super(InlineObjectActionMixin, self).post(request, *args, 
                                                        **kwargs)


class InlineCTObjectActionMixin(InlineObjectActionMixin):

    def get_object(self):

        return get_object_by_ctype_id(self.kwargs['ctype'], self.kwargs['id'])
    
