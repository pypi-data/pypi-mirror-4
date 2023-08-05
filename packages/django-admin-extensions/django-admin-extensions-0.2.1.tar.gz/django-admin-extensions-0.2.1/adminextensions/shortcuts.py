from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template.defaultfilters import truncatewords
from django.utils.html import escape


def model_search(text, model, args):

    app_label = model._meta.app_label
    module_name = model._meta.module_name

    url_name = 'admin:%s_%s_changelist' % (app_label, module_name)

    def tool(context):

        url = reverse(url_name)

        qd = QueryDict(None, mutable=True)
        qd.update(args(context['original']))

        query_string = qd.urlencode()
        search_url = url + '?' + query_string

        return print_link(text, search_url, "model_search")
    return tool


def model_link(text, model, pk_getter, action="change"):

    app_label = model._meta.app_label
    module_name = model._meta.module_name

    url_name = 'admin:%s_%s_change' % (app_label, module_name)

    def tool(context):
        pk = pk_getter(context['original'])
        if pk:
            url = make_admin_url(model, pk=pk, action=action)
            return print_link(text, url, "model_search")
        else:
            return ''
    return tool


def make_admin_url(model, pk=None, action="change"):
    app_label = model._meta.app_label.lower()
    module_name = model._meta.module_name
    url_name = "admin:%s_%s_%s" % (app_label, module_name, action)

    if pk is None:
        pk = model.pk

    url = reverse(url_name, args=(pk,))
    return url


def link_field(field, action="change", formatter=unicode,
               short_description=None):

    if short_description is None:
        short_description = field

    def item(obj):
        related = getattr(obj, field)

        url = make_admin_url(related, action=action)
        name = formatter(related)

        link = print_link(escape(name), url)

        return link

    item.short_description = short_description
    item.allow_tags = True
    return item


def serialized_many_to_many_field(field, formatter=escape, joiner=', ',
                                  short_description=None, linked=False):
    if short_description is None:
        short_description = field

    if linked:
        old_formatter = formatter
        formatter = lambda obj: print_link(old_formatter(obj), make_admin_url(obj))

    item = lambda obj: joiner.join(formatter(x) for x in getattr(obj, field).all())
    item.allow_tags = True
    item.short_description = short_description

    return item


def truncated_field(field, length=20, short_description=None):
    if short_description is None:
        short_description = field

    item = lambda obj: truncatewords(getattr(obj, field), length)
    item.short_description = short_description
    return item


def print_link(text, url, class_name=""):
    return u'<a href="%s" class="%s">%s</a>' % (url, class_name, text)
