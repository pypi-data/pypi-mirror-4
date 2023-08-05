from django.contrib import admin


def extend(base, extra):
    if extra is None:
        return base

    base = base or {}
    base.update(extra)
    return base


class ExtendedModelAdmin(admin.ModelAdmin):

    object_tools = {
        'add': [],
        'change': [],
        'changelist': [],
    }

    add_form_template = 'adminextensions/change_form.html'
    change_form_template = 'adminextensions/change_form.html'
    change_list_template = 'adminextensions/change_list.html'

    valid_lookups = ()

    def get_object_tools(self, request, method):
        return self.object_tools.get(method, None)

    def add_view(self, request, form_url='', extra_context=None):
        object_tools = self.get_object_tools(request, 'add')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).add_view(
            request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        object_tools = self.get_object_tools(request, 'change')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).change_view(
            request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        object_tools = self.get_object_tools(request, 'changelist')
        extra_context = extend(extra_context, {'object_tools': object_tools})
        return super(ExtendedModelAdmin, self).changelist_view(
            request, extra_context)

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(ExtendedModelAdmin, self).lookup_allowed(
            lookup, *args, **kwargs)
