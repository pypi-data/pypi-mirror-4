from django import template
from europeana.query import query
from django.template import Context, Node, Variable, TemplateSyntaxError
import pprint
from django.template.loader import get_template
import collections

register = template.Library()

@register.simple_tag
def europeana_simple(parameter):
    data = query([('what',parameter)])
    return get_template('europeana/data.html').render(Context({
        'items': data['items'],
        'count': data['count'],
        'json': data['json'],
    }))

@register.tag('europeana')
class EuropeanaSearchNode(Node):
    def __init__(self, parser, token):
        nodelist = parser.parse(('endeuropeana',))
        parser.delete_first_token()
        self.nodelist = nodelist
        self.lookup = {}
    def render(self, context):
        lookup_array = []
        filters = []
        for node in self.nodelist:
            if isinstance(node, EuropeanaSearchParameterNode):
                node.resolve(context)
                if node.resolved_data is None:
                    continue
                filter_active = context['request'].GET.get('filter_%s' % node.resolved_label) or not context['request'].GET.get('filters')
                if filter_active:
                    lookup_array.append((node.resolved_parameter, node.resolved_data))
                filters.append({'label': node.resolved_label, 'checked': filter_active })
        data = query(lookup_array)
        return get_template('europeana/data.html').render(Context({
            'items': data['items'],
            'count': data['count'],
            'json': data['json'],
            'filters': filters,
        }))


@register.tag('europeana_parameter')
class EuropeanaSearchParameterNode(Node):
    def __init__(self, parser, token):
        try:
            tag_name, parameter, data, label = token.split_contents()
        except ValueError:
            raise TemplateSyntaxError("%r tag requires exactly three arguments: europeana_field, search query, label. " % 
                                      token.contents.split()[0])
        self.parameter = parameter
        self.data = data
        self.label = label
    def resolve(self, context):
        self.resolved_parameter = Variable(self.parameter).resolve(context)
        self.resolved_data = Variable(self.data).resolve(context)
        self.resolved_label = Variable(self.label).resolve(context)
    def render(self, context):
        self.resolve(context)
        if self not in context.render_context:
            context.render_context[self] = (self.resolved_parameter, self.resolved_data, self.resolved_label)
        return ''