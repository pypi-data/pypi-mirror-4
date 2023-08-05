from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils import simplejson as json
from selectable.base import (LookupBase as SelectableLookupBase,
        ModelLookup as SelectableModelLookup)


class LookupBase(SelectableLookupBase):

    max_limit = 100

    def results(self, request):
        results = {}
        form = self.form(request.GET)
        if form.is_valid():

            options = self._get_options(form)
            term, limit = options['term'], options['limit']
            raw_data = self.get_query(request, term)
            page_data = self.paginate_results(request, raw_data, limit)
            results = self.format_results(page_data, options)

        content = self.get_content(results)
        return self.get_response(content, 'application/json')

    def _get_options(self, valid_form):
        '''
        Returns a dictionary of options from a valid lookup form instance.
        `term` and `limit` are required
        '''
        term = valid_form.cleaned_data.get('term', '')
        limit = valid_form.cleaned_data.get('limit', self.max_limit)

        # check if provided limit isn't bigger than max_limit
        if limit and self.max_limit and limit > self.max_limit:
            limit = self.max_limit

        return {'term' : term, 'limit' : limit}

    def format_results(self, page_data, options):
        '''
        Returns a python structure that later gets serialized.
        page_data
            list of objects that where queried
        options
            a dictionary of the given options
        '''
        results = {}
        meta = options.copy()

        if page_data and hasattr(page_data, 'has_next') and page_data.has_next():
            meta.update( {
                'next_page': page_data.next_page_number(),
            })
        if page_data and hasattr(page_data, 'has_previous') and page_data.has_previous():
            meta.update( {
                'prev_page': page_data.previous_page_number(),
            })

        data = []
        obj_list = page_data.object_list
        for item in obj_list:
            data.append(self.format_item(item))

        results['data'] = data
        results['meta'] = meta

        return results

    def get_content(self, results):
        '''
        Returns serialized results for sending via http.
        '''
        return json.dumps(results, cls=DjangoJSONEncoder, ensure_ascii=False)

    def get_response(self, content, content_type='application/json'):
        '''
        Returns a HttpResponse with the given content and content_type.
        '''
        return HttpResponse(content, content_type=content_type)


class ModelLookup(LookupBase, SelectableModelLookup):
    pass
