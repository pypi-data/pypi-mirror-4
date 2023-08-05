from selectable.forms.widgets import AutoCompleteWidget
from django.conf import settings

from django.utils import simplejson as json


__all__ = ('AutoCompleteSelect2Widget',)

MEDIA_URL = settings.MEDIA_URL
STATIC_URL = getattr(settings, 'STATIC_URL', u'')
MEDIA_PREFIX = u'{0}selectable_select2/'.format(STATIC_URL or MEDIA_URL)

# these are the kwargs that u can pass when instantiating the widget
TRANSFERABLE_ATTRS = ('placeholder', 'initialselection', 'parent_ids', 'clearonparentchange', 'parent_namemap')

# a subset of TRANSFERABLE_ATTRS that should be serialized on "data-djsels2-*" attrs
SERIALIZABLE_ATTRS = ('clearonparentchange',)

# a subset of TRANSFERABLE_ATTRS that should be serialize on "data-*" attrs
EXPLICIT_TRANSFERABLE_ATTRS = ('placeholder',)


class SelectableSelect2MediaMixin(object):

    class Media(object):
        css = {
            'all': (u'{0}css/select2.css'.format(MEDIA_PREFIX),)
        }
        js = (
            u'{0}js/jquery.django.admin.fix.js'.format(MEDIA_PREFIX),
            u'{0}js/select2.min.js'.format(MEDIA_PREFIX),
            u'{0}js/jquery.dj.selectable.select2.js'.format(MEDIA_PREFIX),
        )


class Select2BaseWidget(SelectableSelect2MediaMixin, AutoCompleteWidget):

    def __init__(self, *args, **kwargs):
        for attr in TRANSFERABLE_ATTRS:
            setattr(self, attr, kwargs.pop(attr, ''))

        super(Select2BaseWidget, self).__init__(*args, **kwargs)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(Select2BaseWidget, self).build_attrs(extra_attrs, **kwargs)

        for real_attr in TRANSFERABLE_ATTRS:
            attr = real_attr.replace('_', '-')
            value = getattr(self, real_attr)

            # because django widget can't properly output json in his attrs
            # so we're flattening the map into string of comma delimitted strings
            # in form "key0,value0,key1,value1,..."
            if real_attr == 'parent_namemap':
                if isinstance(value, dict):
                    value_copy = value.copy()
                    value = []
                    for k, v in value_copy.items():
                        value.extend([k, v])
                value = ",".join(value)

            if real_attr in SERIALIZABLE_ATTRS:
                value = json.dumps(value)
            attrs[u'data-djsels2-' + attr] = value
            if real_attr in EXPLICIT_TRANSFERABLE_ATTRS:
                attrs[u'data-' + attr] = value

        attrs[u'data-selectable-type'] = 'select2'

        return attrs

    def render(self, name, value, attrs=None):
        # when there is a value and no initialselection was passed to the widget
        if value is not None and (self.initialselection is None or self.initialselection == ''):
            lookup = self.lookup_class()
            item = lookup.get_item(value)
            if item is not None:
                initialselection = lookup.get_item_value(item)
                self.initialselection = initialselection
        return super(Select2BaseWidget, self).render(name, value, attrs)


class AutoCompleteSelect2Widget(Select2BaseWidget):
    pass
