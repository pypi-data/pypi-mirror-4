django-selectable-select2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    This is still a work in progress. Some backwards incompatible changes may happen between releases.

This project is a kind of a plugin for `django-selectable`_.

It provides widgets for use with a great JS library called `select2`_ rather than jQuery UI.

For now there's only a basic single-valued autocomplete widget for usage on ForeignKey (or simply ModelChoiceField) fields.

Installation
=============


* install `django-selectable`_ (you can ommit the part regarding jquery-ui)

* install `django-selectable-select2` like so::

    pip install django-selectable-select2

* add `selectable_select2` to `INSTALLED_APPS`. So it look like this::

    INSTALLED_APPS = (
        ...
        'selectable',
        'selectable_select2',
        ...
    )

* add/change a setting ``SELECTABLE_ESCAPED_KEYS`` like this::

    SELECTABLE_ESCAPED_KEYS = ('label', 'value')


Usage
============

* define your `lookup class`_

.. warning::
    as for now (until `issue #64`_ is resolved) you should inherit from ``selectable_select2.base.LookupBase`` and ``selectable_select2.base.ModelLookup``

* in your forms you can use ``selectable_select2.widgets.AutoCompleteSelect2Widget`` like so::

    from selectable_select2.widgets import AutoCompleteSelect2Widget
    from django import forms

    from myapp.models import MyModel  # example model with a ForeignKey called ``myfk``
    from myapp.lookups import MyModelLookup  # the lookup defined in previous step

    class MyModelForm(forms.ModelForm):

        class Meta:
            model = MyModel
            widgets = {
                'myfk' : AutoCompleteSelect2Widget(MyModelLookup, placeholder='select related item')
            }

How to include static assets?
----------------------------------

There are at least 2 ways of including static assets to work with django-selectable-select2.
Both of them assumes that jQuery is already included.

* First of all you can use the form's `media` attribute to include appropriate js and css files. Like so::

    <html>
        <head>
            {{ form.media.css }}
        </head>

        <body>
            <form action="." method="post">
                {{ form.as_p }}
                <p><button type="submit">Submit</button></p>
            </form>

            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
            {{ form.media.js }}
        </body>
    </html>

  .. note::
      The ``{{ form.media.js }}`` also includes the ``jquery.django.admin.fix.js`` to work with django admin panel.
      You may not need this.

* Or you can mannually include those assets (assuming you're using django-staticfiles). Like so::

    <html>
        <head>
            <link rel="stylesheet" href="{{ STATIC_URL }}selectable_select2/js/select2.css">
        </head>

        <body>
            <form action="." method="post">
                {{ form.as_p }}
                <p><button type="submit">Submit</button></p>
            </form>

            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}selectable_select2/js/select2.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}selectable_select2/js/jquery.dj.selectable.select2.js"></script>
        </body>
    </html>

Chained selects
----------------

There is a way to do chained selects in `django-selectable`.
Check out the `docs about chained selects`_ to correctly prepare your lookup classes
for this use case (you can skip the javascript part).
Django-selectable-select2 provides a helper class to declare dependencies of your chained selects
on your form.

So given the lookup, from the above link and assuming that MyModel has ForeignKeys
for city and state, your form class can inherit from ``Select2DependencyModelForm``
and define ``select2_deps`` attribute like this::

    from selectable_select2.forms import Select2DependencyModelForm
    from django import forms
    from selectable_select2.widgets import AutoCompleteSelect2Widget

    class ChainedForm(Select2DependencyModelForm):

        select2_deps = (
            ('city', { 'parents' : ['state'] }),
        )

        class Meta:
            model = MyModel
            widgets = {
                'city' : AutoCompleteSelect2Widget(CityLookup, placeholder='select city')
            }

There is also ``Select2DependencyForm`` which is suitable for non-model based forms.

.. note::
    Both ``Select2DependencyModelForm`` and ``Select2DependencyForm``
    in ``selectable_select2.forms`` module inherit from a general class called
    ``Select2DependencyFormMixin`` which defines one method called ``apply_select2_deps``.
    Don't hesitate to browse the source of those classes.


``select2_deps`` is a tuple of two-tuples in form `('<fieldname>' : { <options dict> })`
where the `options dict` is a Python dictionary that configurates the dependencies for that field.

Reference for the `options dict`:

parents
    List of field names that are superior for the given field.
    Like in the above example you can choose a `city` depending on what `state` you've chosen.
    The field can be dependant from more than one parent. Defaults to: **[]**.

clearonparentchange
    Boolean (True/False) that indicates whether a field should be cleared when a user
    changes the selection/value of one of it's parents. Defaults to: **True**.

parents_namemap
    A convenient option (python dictionary) for indicating which key name is sent via ajax for which parent.
    E.g. Assume that field ``child`` depends on ``parent1`` and ``parent2`` in our
    chained selects. You can specify::

        select2_deps = (
            ('child', {
                parents : ['parent1', 'parent2' ]
                parents_namemap : { 'parent1' : 'parent', 'parent2' : 'parent' }
            }),
        )

    Then your lookup can be cleaner and you can search only for ``parent`` key
    instead of juggling with ``parent1`` and ``parent2`` in your ``get_query``
    method. Defaults to: **{}**.

Check the `example` project for more details.


TODO
======

check out `TODO.rst`

A note about version of django-selectable
===========================================

The minimal version of django-selectable that is required for this app is
0.6

A note about version of select2.js used here
==============================================

django-selectable-select2 comes bundled with "unstable" version of `select2`_.
This version is above commit `7baa3b9e9`_ (the unstable and unreleased 3.2 version)
where you can provide your own function to escape the markup.
If you want to use this version (e.g. on other select widgets in your project) do it like this::

    <script src="{{ STATIC_URL }}selectable_select2/js/select2.min.js"></script>

See https://github.com/ivaynberg/select2/pull/355 for details.

Credits
==========

A BIG THANK YOU goes to `Igor Vaynberg`_ (`select2`_) and `Mark Lavin`_ (`django-selectable`_)
for their projects, their support and quick response time in resolving my issues.

.. _Igor Vaynberg: https://github.com/ivaynberg
.. _Mark Lavin: https://bitbucket.org/mlavin

.. _docs about chained selects: http://django-selectable.readthedocs.org/en/latest/advanced.html#chained-selection
.. _7baa3b9e9: https://github.com/ivaynberg/select2/commit/7baa3b9e93690b7dacad8fbb22f71b8a3940e04d
.. _django-selectable: https://bitbucket.org/mlavin/django-selectable
.. _select2: http://ivaynberg.github.com/select2/index.html
.. _lookup class: http://django-selectable.readthedocs.org/en/latest/lookups.html
.. _issue #64: https://bitbucket.org/mlavin/django-selectable/issue/64/decouple-building-results-from

