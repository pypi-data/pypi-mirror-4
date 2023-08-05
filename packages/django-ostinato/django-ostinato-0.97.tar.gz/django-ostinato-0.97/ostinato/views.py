from django import http
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json


class AjaxTemplateResponseMixin(object):
    template_name = None
    xhr_template_name = None

    def get_template_names(self):
        if self.request.is_ajax():
            self.template_name = self.xhr_template_name
        return super(AjaxTemplateResponseMixin, self).get_template_names()


class JsonMixin(object):

    def get(self, *args, **kwargs):
        # Note the use of the DjangoJSONEncoder here, this handles date/time
        # and Decimal values correctly
        data = json.dumps(self.get_values(**kwargs), cls=DjangoJSONEncoder)
        return http.HttpResponse(data, content_type='application/json; charset=utf-8')

        
# class JSONMixin(object):

#     def render_to_response(self, context):
#         response =  http.HttpResponse(
#             json.dumps(self.get_data(data), cls=DjangoJSONEncoder),
#             content_type='application/json; charset=utf-8')
#         response['Cache-Control'] = 'no-cache, no-store, must-revalidate, post-check=0, pre-check=0'
#         response['Pragma'] = 'no-cache'
#         return http.HttpResponse()

