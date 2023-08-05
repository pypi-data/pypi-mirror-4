import json

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from djangolytics.models import ModelKlass

TOKEN = settings.DJANGOLYTICS.get("TOKEN", )

VALID_QUERY_NAMES = ('choices', 'created', 'modified', 'test')

class DjangolyticsView(View):

    def get(self, request, *args, **kwargs):

        # Check if token is authenticated
        token = self.request.GET.get('token', '')
        if token != TOKEN:
            msg = "Bad Authentication Token"
            response = HttpResponse(json.dumps({'error': msg}))
            response.status_code = 401
            return response
        
        # Check to make sure the query is valid, default to choices
        query = self.request.GET.get('query', 'choices')
        if query not in VALID_QUERY_NAMES:
            msg = "Invalid query: please choose 'choices', 'created', 'modified', or 'test'."
            response = HttpResponse(json.dumps({'error': msg}))
            response.status_code = 403
            return response
        
        if query == 'test':
            msg = "Test query successful"
            response = HttpResponse(json.dumps({'test': msg}))
            return response
        
        # Get the MODEL_NAME and list of MODELS for querying.
        MODEL_NAME = "{0}_MODELS".format(query.upper())
        MODELS = settings.DJANGOLYTICS.get(MODEL_NAME, ())

        # Get the query method name for hitting ModelKlass query methods
        query_method_name = "query_{0}".format(query)
        
        # Build the dataset
        datasets = {}
        for model in MODELS:
            model_klass = ModelKlass(model)
            query_method = getattr(model_klass, query_method_name)
            datasets[model_klass.app_model] = query_method()
        return HttpResponse(json.dumps(datasets))