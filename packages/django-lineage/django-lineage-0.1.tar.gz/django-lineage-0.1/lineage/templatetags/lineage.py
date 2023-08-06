# This is where the cool stuff lives

import re

from django import template
from django.template.defaulttags import url

register = template.Library()


@register.tag
def ifanscestor(parser, token):
    """
    Returns the contents of the tag if the provided path consitutes the
    base of the current pages path.

    There are two ways to provide arguments to this tag. Firstly one may
    provide a single argument that starts with a forward slash. e.g.

        {% ifanscestor '/path/to/page' %}...{% endifanscestor}
        {% ifanscestor path_variable %}...{% endifanscestor}

    In this case the provided path will be used directly.

    Alternatively any arguments accepted by the standard "url" tag may
    be provided. They will be passed to the url tag and the resultant
    path will be used. e.g.

        {% ifanscestor 'core:model:detail' model.pk %}...{% endifanscestor}

    Ultimately the provided path is matched against the path of the
    current page. If the provided path is found at the root of the current
    path it will be considered an anscestor, and the contents of this tag
    will be rendered.

    """
    # Grab the contents between
    contents = parser.parse(('endifanscestor',))
    parser.delete_first_token()

    # If there is only one argument (2 including tag name)
    # parse it as a variable
    bits = token.split_contents()
    if len(bits) == 2:
        arg = parser.compile_filter(bits[1])
    else:
        arg = None

    # Also pass all arguments to the original url tag
    url_node = url(parser, token)

    # Send both the fir
    return NavNode(arg, url_node, contents)


class NavNode(template.Node):
    def __init__(self, arg, url_node, contents):
        self.arg = arg
        self.url_node = url_node
        self.contents = contents

    def get_path(self, context):
        # If the singular argument was provided and starts with a forward
        # slash, use it as the path
        if self.arg is not None:
            arg_output = self.arg.resolve(context)
            if re.match('/', arg_output):
                return arg_output

        # Otherwise derive the path from the url tag approach
        return self.url_node.render(context)

    def render(self, context):
        # Get the path of the current page (requires that "request" be
        # in the context)
        current_path = context['request'].path

        path = self.get_path(context)

        # If the provided path is found at the root of the current path
        # render the contents of this tag
        if re.match(path, current_path):
            return self.contents.render(context)
        return ''
