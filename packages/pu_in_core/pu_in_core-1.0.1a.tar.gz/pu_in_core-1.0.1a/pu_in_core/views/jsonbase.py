from django import http
from django.utils import simplejson as json
from django.template.loader import render_to_string


class JSONResponseMixin(object):

    template_name = None

    def render_html(self, context, template=None):

        """ Override this so as to return an actual html
        template. This will be added to the JSON data under the key of
        'html'.
        """

        if not template:
            template = self.template_name

        return template and render_to_string(template, context) or ""

    def get_context_data(self, **kwargs):

        """ Base implementation that just returns the view's kwargs """

        kwargs['request'] = self.request

        return kwargs

    def render_to_response(self, context, template=None, **response_kwargs):
        
        "Returns a JSON response containing 'context' as payload"

        context['html'] = self.render_html(context, template=template)

        return http.HttpResponse(
            json.dumps(context, skipkeys=True,
                       default=lambda x: "NOT SERIALIZABLE"),
            content_type='application/json',
            **response_kwargs)


class JSONFormMixin(JSONResponseMixin):

    success_template_name = None

    def form_valid(self, form):

        self.object = form.save()
        return self.render_to_response(
            self.get_context_data(form=form, object=self.object),
            template=self.success_template_name)

    def get_context_data(self, **kwargs):

        context = super(JSONFormMixin, self).get_context_data(**kwargs)

        context['action'] = self.request.path

        return context
