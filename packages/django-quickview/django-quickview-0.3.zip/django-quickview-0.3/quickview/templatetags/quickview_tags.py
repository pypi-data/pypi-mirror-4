from django.core.urlresolvers import reverse
from django import template
from django.core.context_processors import csrf

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.inclusion_tag('quickview/template_inclusion.js', takes_context=True)
def qv_inclusion(context, app_label, model_names):
    csrf_token = csrf(context['request']).get('csrf_token', None)
    return {'csrf_token': csrf_token, 'app_label': app_label, 'model_names': [mn.strip() for mn in model_names.split(',')]}

@register.tag
def quickview_ajax_api(parser, token):
    try:
        parts = token.split_contents()
        app_label = parts[1]
        model_names = parts[2:]
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires at least two arguments" % token.contents.split()[0])

    return FormatApiNode(app_label, model_names)

class FormatApiNode(template.Node):

    def __init__(self, app_label, model_names):
        self.model_names = model_names
        self.app_label = app_label

    def render(self, context):
        try:
            csrf_token = csrf(context['request']).get('csrf_token', None)
            html = []
            for model_name in self.model_names:
                html.append('   <script type="text/javascript" src="%(api_url)s"></script>' % {'api_url': reverse('%s-%s-api' % (self.app_label, model_name.lower()))})
            html.append('       <script type="text/javascript">')
            for model_name in self.model_names:
                html.append("           var %(model_name)sApi = new _%(model_name)sApi('%(csrf_token)s');" % {
                    'model_name': model_name,
                    'csrf_token': csrf_token,
                    'app_label': self.app_label,
                })

            html.append("       </script>")
            return "\n".join(html)
        except template.VariableDoesNotExist:
            return 'Nothing'
