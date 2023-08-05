==================
django-markitup-field
==================

An implementation of a custom MarkupField for Django.  A MarkupField is in
essence a TextField with an associated markup format and `MarkItUp!`_ markup
editor widget with AJAX preview.  The field also caches its rendered value on
the assumption that disk space is cheaper than CPU cycles in a web application.

Based on `django-markupfield <https://github.com/jamesturk/django-markupfield>`_
and `django-markitup <https://github.com/carljm/django-markitup>`_.

.. _MarkItUp!: http://markitup.jaysalvat.com/

Installation
============

The recommended way to install django-markitup-field is with
`pip <http://pypi.python.org/pypi/pip>`_

Install from PyPI with ``easy_install`` or ``pip``::

    pip install django-markitup-field

or get the `in-development version`_::

    pip install django-markitup-field==tip

.. _in-development version: https://github.com/dimka665/django-markitup-field

It is not necessary to add ``'markitup_field'`` to your ``INSTALLED_APPS``, it
merely needs to be on your ``PYTHONPATH``.

If you want to use AJAX-based preview, add
``url(r'^markitup/', include('markitup.urls'))`` in your root URLconf.

Requirements
------------

django-markitup-field depends on a relatively current version of Django
(tested with 1.3-1.4, may work with 1.2 but not guaranteed) and libraries for
whichever markup options you wish to include.


Settings
========

You can define the ``MARKUP_FILTERS`` setting, a mapping of strings
to callables that 'render' a markup type::

    import markdown
    from docutils.core import publish_parts

    def render_rest(markup):
        parts = publish_parts(source=markup, writer_name="html4css1")
        return parts["fragment"]

    MARKUP_FILTERS = (
        ('markdown', markdown.markdown),
        ('restructuredtext', render_rest),
    )

If you do not define a ``MARKUP_FILTERS`` then one is provided with the
following markup types available:

html:
    allows HTML, potentially unsafe
text:
    plain text markup, calls urlize and replaces text with linebreaks
markdown:
    default `markdown`_ renderer (only if `python-markdown`_ is installed)
restructuredtext:
    default `ReST`_ renderer (only if `docutils`_ is installed)
textile:
    default `textile`_ renderer (only if `textile`_ is installed)

.. _`markdown`: http://daringfireball.net/projects/markdown/
.. _`ReST`: http://docutils.sourceforge.net/rst.html
.. _`textile`: http://hobix.com/textile/quick.html
.. _`python-markdown`: http://www.freewisdom.org/projects/python-markdown/
.. _`docutils`: http://docutils.sourceforge.net/
.. _`python-textile`: http://pypi.python.org/pypi/textile

Usage
=====

Using MarkupField is relatively easy, it can be used in any model definition::

    from django.db import models
    from markitup_field.fields import MarkupField

    class Article(models.Model):
        title = models.CharField(max_length=100)
        slug = models.SlugField(max_length=100)
        body = MarkupField()

``Article`` objects can then be created with any markup type defined in
``MARKUP_FORMATS``::

    Article.objects.create(title='some article', slug='some-article',
                           body='*fancy*', body_markup_format='markdown')

You will notice that a field named ``body_markup_format`` exists that you did
not declare, MarkupField actually creates two extra fields. ``body_markup_format``
This field is always named according to the name of the declared ``MarkupField``.

Arguments
---------

``MarkupField`` also takes three optional arguments.  Either
``default_markup_format`` and ``markup_format`` arguments may be specified but
not both.

``default_markup_format``:
    Set a markup_type that the field will default to if one is not specified.
    It is still possible to edit the markup type attribute and it will appear
    by default in ModelForms.

``markup_format``:
    Set markup type that the field will always use, ``editable=False`` is set
    on the hidden field so it is not shown in ModelForms.

``markup_choices``:
    A replacement list of markup choices to be used in lieu of
    ``MARKUP_FORMATS`` on a per-field basis.

``escape_html``:
    A flag (False by default) indicating that the input should be regarded
    as untrusted and as such will be run through Django's ``escape`` filter.

``rendered_field_name``:
    Name for field with rendered content. If it is set to None, then it named <field_name>_rendered


Examples
~~~~~~~~

``MarkupField`` that will default to using markdown but allow the user a choice::

    MarkupField(default_markup_type='markdown')

``MarkupField`` that will use textile and not provide a choice on forms::

    MarkupField(markup_type='textile')

``MarkupField`` that will use a custom set of renderers::

    CUSTOM_RENDERERS = (
        ('markdown', markdown.markdown),
        ('wiki', my_wiki_render_func)
    )
    MarkupField(markup_choices=CUSTOM_RENDERERS)

Accessing a MarkupField on a model
----------------------------------

When accessing an attribute of a model that was declared as a ``MarkupField``
a special ``Markup`` object is returned.  The ``Markup`` object has three
parameters:

``raw``:
    The unrendered markup.
``markup_format``:
    The markup type.
``rendered``:
    The rendered HTML version of ``raw``, this attribute is read-only.

This object has a ``__unicode__`` method that calls
``django.utils.safestring.mark_safe`` on ``rendered`` allowing MarkupField
objects to appear in templates as their rendered selfs without any template
tag or having to access ``rendered`` directly.

Assuming the ``Article`` model above::

    >>> a = Article.objects.all()[0]
    >>> a.body.raw
    u'*fancy*'
    >>> a.body.markup_type
    u'markdown'
    >>> a.body.rendered
    u'<p><em>fancy</em></p>'
    >>> print unicode(a.body)
    <p><em>fancy</em></p>

Assignment to ``a.body`` is equivalent to assignment to ``a.body.raw`` and
assignment to ``a.body_markup_format`` is equivalent to assignment to
``a.body.markup_format``.

.. note::
    a.body.rendered is only updated when a.save() is called

