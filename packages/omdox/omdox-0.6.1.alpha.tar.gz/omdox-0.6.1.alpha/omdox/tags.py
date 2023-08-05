import os
from jinja2 import nodes
from jinja2.ext import Extension
from jinja2 import contextfunction


class NavigationExtension(Extension):
    tags = set(['navigation'])
    
    def __init__(self, environment):
        super(NavigationExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        args = [parser.parse_expression()]
        body = parser.parse_statements(
                ['name:endnavigation'], drop_needle=True)
        return nodes.CallBlock(
                self.call_method('_navigation', args),
               [], [], body).set_lineno(lineno)

    @contextfunction
    def _navigation(self, context, *args,  **kwargs):
        from omdox.models import Tree
        print kwargs
        print context
        context['HOUSE'] = '12'
        print args
        tree = Tree(os.getcwd())
        #tree.grow()

        return ''
        return tree.get_nav(level=level)

