=====
Django-Europeana
=====

Source code: https://github.com/justinasjaronis/django-europeana

It is application that provides template tags for easy Europeana content integration.

Quick start
-----------

1. Add "europeana" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'europeana',
      )

2. Add Europeana API key to the settings.py:

EUROPEANA_API_KEY = '123456677'

3. Add Europeana tags to Your template:

A) Simple version:

	{% load europeana_tags %}
	{% europeana_simple query %}
	
	It will display simple list of Europeana search results provided by query.  

B) Advanced version:

	{% load europeana_tags %}
	{% europeana %}
		{% europeana_param "what" query "Label" %}
		{% europeana_param "who" author "Author" %}
		{% europeana_param "where" place "Location" %}
	{% endeuropeana %}

Query, author, place can be string or list of objects, i.e. Model.objects.all() iterable from manager.
Before query, this app will try to cast all variables in list to string.

5. Voilla! Visit Your template to view results. 

6. Optional settings:

-Add this to Your template head: 

   <link rel="stylesheet" type="text/css" href="{% static "css/object.css" %}/>
   <script src="{% static "js/object.js" %} type="text/javascript"></script>

And JQuery, if You do not have it already present in Your template:
   <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>

This will add some default styling and hover preview image functionality.


EUROPEANA_URI = 'http://www.europeana.eu/api/v2/search.json' 
- URI that is queried via webservice. Not likely to change, though, not hardcoded :-)

EUROPEANA_EXCLUDE_QUERY = ''
- Query that allows exclusion of results, in example, if the contents of database is already imported.

7. Template to override:

europeana/data.html : 
You get these three variables for sure:
 - count: number of results
 - items: dict with normalized results from Europeana (casted to string). Possible values:
     'title': title of the irem,
     'guid': URL to the item in Europeana
     'link': URL to the JSON to item details
     'year': year of the results
     'provider': provider
     'data_provider': data provider of the item
     'europeanaCompleteness': completeness index of current item
     'preview': URL of preview image
 - json: pure JSON from Europeana  
 
8. TODO:
- Implement way to cache/resize images for preview (because they are too big to display)
- Implement conditional multiple query parameters filtering (now it's only AND)
- Clean filter checkbox rendering and request parameter parsing (should be implemented to 
		generate a form, display a form nicely and add some unique widget variable to the form)
- Implement search result caching
- Implement search result prefetching (i.e. nightly for most popular objects)

