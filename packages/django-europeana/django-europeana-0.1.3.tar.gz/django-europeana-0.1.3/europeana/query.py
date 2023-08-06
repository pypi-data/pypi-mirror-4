# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
import urllib2
import json
from django.conf import settings


# query_parameters is a tuple, consisting of:
# (europeana_field, filter_value)
# filter value can be either string or list of strings.
def query(query_parameters):
    EUROPEANA_API_KEY = getattr(settings, 'EUROPEANA_API_KEY', None)
    EUROPEANA_EXCLUDE_QUERY = getattr(settings, 'EUROPEANA_EXCLUDE_QUERY', None)
    EUROPEANA_URI = getattr(settings, 'EUROPEANA_URI', 'http://www.europeana.eu/api/v2/search.json')

    if not query_parameters:
        return dict(count=0, items=[], json = {})
    
    if EUROPEANA_API_KEY is None:
        raise Exception('EUROPEANA_API_KEY setting is not provided!')
    #Normalize results to simplier structure.
    def check(item, key):
        if item.has_key(key):
            y = item[key]
        else:
            return ''
        if isinstance(y, list):
             return u', '.join(y)
        return y

    #Build query parameter counterpart from list either string
    def query_item(item):
        if isinstance(item[1], list):
            it = []
            
            # Cast all items to string
            for i in item[1]:
                it.append(unicode(i))
                
            return u'%s:(%s)' % (item[0], u' OR '.join(u'"%s"' % (it,)))
        return u'%s:"%s"' % (item[0], unicode(item[1]))
    
    #form the final query
    final_query = '&query='.join([query_item(i) for i in query_parameters])

    url = u'%s?wskey=%s&qf=%s' % ( EUROPEANA_URI, EUROPEANA_API_KEY, final_query, )
    if EUROPEANA_EXCLUDE_QUERY is not None:
        url = u'%s?wskey=%s&qf=%s&query=%s' % ( EUROPEANA_URI, EUROPEANA_API_KEY, final_query, EUROPEANA_EXCLUDE_QUERY)
    else:
        url = u'%s?wskey=%s&query=%s' % ( EUROPEANA_URI, EUROPEANA_API_KEY, final_query, )
    
    print url
    #Convert all spaces to %20, because otherwise Europeana interprets them as "+"
    url = url.replace(' ', '%20')

    print url
    
    request = urllib2.Request(url.encode('utf-8'))
    response = urllib2.urlopen(request)
    html = response.read()
    results_json = json.loads(html)
    total_count = results_json['totalResults']

    if (total_count == 0):
        total = dict(count=total_count, items=[], json = results_json)
    else:
        results = [{
            'type': item['type'],
            'title': check(item,'title'),
            'guid': check(item, 'guid'),
            'link': check(item, 'link'),
            'year': check(item, 'year'),
            'provider': check(item, 'provider'),
            'data_provider': check(item, 'dataProvider'),
            'europeanaCompleteness': check(item, 'europeanaCompleteness'),
            'preview': check(item,'edmPreview'),
        } for item in results_json['items']]
        total = dict(count=total_count, items=results, json = results_json)
    
    return total
