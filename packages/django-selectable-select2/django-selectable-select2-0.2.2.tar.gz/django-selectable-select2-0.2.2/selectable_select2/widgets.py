from selectable.forms.widgets import AutoCompleteWidget
from django.conf import settings

from django.utils import simplejson as json


__all__ = ('AutoCompleteSelect2Widget',)

MEDIA_URL = settings.MEDIA_URL
STATIC_URL = getattr(settings, 'STATIC_URL', u'')
MEDIA_PREFIX = u'{0}selectable_select2/'.format(STATIC_URL or MEDIA_URL)

# these are the kwargs that u can pass when instantiating the widget
TRANSFERABLE_ATTRS = ('placeholder', 'initial_selection', 'parents', 'clearonparentchange')

# a subset of TRANSFERABLE_ATTRS that should be serialized on "data-*" attrs
SERIALIZABLE_ATTRS = ('clearonparentchange',)


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
            if real_attr in SERIALIZABLE_ATTRS:
                value = json.dumps(value)
            attrs[u'data-' + attr] = value

        attrs[u'data-selectable-type'] = 'select2'

        return attrs

    def render(self, name, value, attrs=None):
        # when there is a value and no initial_selection was passed to the widget
        if value is not None and (self.initial_selection is None or self.initial_selection == ''):
            lookup = self.lookup_class()
            item = lookup.get_item(value)
            if item is not None:
                initial_selection = lookup.get_item_value(item)
                self.initial_selection = initial_selection
        return super(Select2BaseWidget, self).render(name, value, attrs)


class AutoCompleteSelect2Widget(Select2BaseWidget):
    pass
