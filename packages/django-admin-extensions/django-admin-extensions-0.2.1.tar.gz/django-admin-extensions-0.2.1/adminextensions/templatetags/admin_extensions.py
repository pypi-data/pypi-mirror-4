from django import template

register = template.Library()

@register.tag
def object_tool(parser, token):
    return ObjectToolNode.handle(parser, token)

class ObjectToolNode(template.Node):

    @classmethod
    def handle(cls, parser, token):
        bits = token.split_contents()
        tool = bits[1]
        return cls(tool)

    def __init__(self, tool):
        self.tool = tool

    def render(self, context):
        tool = context[self.tool]
        link = tool(context)
        if link:
            return '<li>%s</li>' % link
        else:
            return ''
