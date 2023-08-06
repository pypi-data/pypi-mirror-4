"""
This set of templatetags are used to show graph in any pages of your project.
"""

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
register = template.Library()


def do_graph_node(parser, token):
    """
    render a GraphNode with the right parameters
    """
    try:
        arguments = token.contents.split()
        method = arguments[1]
        args = arguments[2:]
    except IndexError:
        raise template.TemplateSyntaxError, """
%r tag requires at least 1 argument, the name of the graph you want to render
""".format(token.contents.split()[0])
    return GraphNode(method, *args)


class GraphNode(template.Node):
    def __init__(self, method, *args):
        self.method = template.Variable(method)
        self.args = args
        self. obj = None

    def render(self, context):
        backend = __import__(
            settings.GRAPH_BACKEND,
            fromlist=["Backend"])
        klass = getattr(backend, "Backend")
        try:
            name = self.method.resolve(context)
        except template.VariableDoesNotExist:
            name = unicode(self.method)
        self.obj = klass(name=name,
                         *self.args)

        t = template.loader.get_template(
            'mustachebox/tags/{0}.html'.format(self.obj.template))

        return t.render(
            template.Context(
                {'object': self.obj,
                 "STATIC_URL": context['STATIC_URL']},
                autoescape=context.autoescape))

register.tag('graph', do_graph_node)


@register.filter(name='parse_docstring')
def parse_docstring(value):

    from docutils import core
    publish_args = {'source': value, 'writer_name': 'html4css1'}
    parts = core.publish_parts(**publish_args)
    return mark_safe(parts['fragment'])
