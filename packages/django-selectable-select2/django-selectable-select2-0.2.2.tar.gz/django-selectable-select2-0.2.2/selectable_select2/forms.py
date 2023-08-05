from django import forms
from selectable_select2.widgets import AutoCompleteSelect2Widget


class Select2DependencyFormMixin(object):

    # a tuple of two-tuples of dependencies in form:
    # ('<fieldname>', { 'parents' : ['list', 'of', 'parent', fieldnames'], 'clearonparentchange' : True/False })
    select2_deps = tuple()

    def apply_select2_deps(self):
        for field, opts in self.select2_deps:
            parents_list = []
            fo  = self.fields[field]  # get a field object
            #bfo = self[field]         # get a bound field object
            if not isinstance(fo.widget, AutoCompleteSelect2Widget):
                raise ValueError("Widget on field {0} is not a subclass of {1}".format(field, AutoCompleteSelect2Widget.__name__))

            for parent_fname in opts.get('parents', []):
                parents_list.append(self[parent_fname].auto_id)  # from a bound field get an HTML id
            fo.widget.parents = ",".join(parents_list)
            fo.widget.clearonparentchange = bool(opts.get('clearonparentchange', True))


class Select2DependencyForm(Select2DependencyFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        super(Select2DependencyForm, self).__init__(*args, **kwargs)
        self.apply_select2_deps()


class Select2DependencyModelForm(Select2DependencyFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(Select2DependencyModelForm, self).__init__(*args, **kwargs)
        self.apply_select2_deps()
