import django
#from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import escape

from markitup_field import widgets
#from markitup_field import markup
from markitup_field import settings

_rendered_field_name = lambda name: '_%s_rendered' % name
_markup_format_field_name = lambda name: '%s_markup_format' % name

# for fields that don't set markup_types: detected types or from settings
#MARKUP_CHOICES = getattr(settings, 'MARKUP_FILTERS', markup.MARKUP_FILTERS)


class Markup(object):

    def __init__(self, instance, field_name, rendered_field_name, markup_format_field_name):
        # instead of storing actual values store a reference to the instance
        # along with field names, this makes assignment possible
        self.instance = instance
        self.field_name = field_name
        self.rendered_field_name = rendered_field_name
        self.markup_format_field_name = markup_format_field_name

    # raw is read/write
    def _get_raw(self):
        return self.instance.__dict__[self.field_name]

    def _set_raw(self, val):
        setattr(self.instance, self.field_name, val)

    raw = property(_get_raw, _set_raw)

    # markup_format is read/write
    def _get_markup_format(self):
        return self.instance.__dict__[self.markup_format_field_name]

    def _set_markup_format(self, val):
#        return setattr(self.instance, self.markup_format_field_name, val)
        setattr(self.instance, self.markup_format_field_name, val)

    markup_format = property(_get_markup_format, _set_markup_format)

    # rendered is a read only property
    def _get_rendered(self):
        return getattr(self.instance, self.rendered_field_name)
    rendered = property(_get_rendered)

    # allows display via templates to work without safe filter
    def __unicode__(self):
        return mark_safe(self.rendered)


class MarkupDescriptor(object):

    def __init__(self, field):
        self.field = field
        self.rendered_field_name = field.rendered_field_name
        self.markup_format_field_name = field.markup_format_field_name

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')
        markup = instance.__dict__[self.field.name]
        if markup is None:
            return None
        return Markup(instance, self.field.name, self.rendered_field_name, self.markup_format_field_name)

    def __set__(self, obj, value):
        if isinstance(value, Markup):
            obj.__dict__[self.field.name] = value.raw
            setattr(obj, self.rendered_field_name, value.rendered)
            setattr(obj, self.markup_format_field_name, value.markup_format)
        else:
            obj.__dict__[self.field.name] = value


class MarkupField(models.TextField):

    def __init__(self, verbose_name=None, name=None,
                 markup_format=None, default_markup_format=None, markup_choices=settings.MARKUP_CHOICES,
                 rendered_field_name=None,
                 escape_html=False, **kwargs):

        if markup_format and default_markup_format:
            raise ValueError("Cannot specify both 'markup_format' and 'default_markup_format'")

        if not default_markup_format:
            default_markup_format = settings.MARKUP_DEFAULT_FORMAT

#        if render_to_field and rendered_field_name:
#            raise ValueError("Cannot specify both 'render_to_field' and 'rendered_field_name'")

#        if render_to_field:
#            render_to_field_class_is_child_of_field = False
#            try:
#                render_to_field_class_is_child_of_field = issubclass(render_to_field.__class__, models.Field)
#            except TypeError:
#                pass
#
#            if not render_to_field_class_is_child_of_field:
#                raise ValueError("'render_to_field' must be Field")

#        self.render_to_field = render_to_field
#        print(render_to_field.)
        self.rendered_field_name = rendered_field_name

        self.default_markup_format = markup_format or default_markup_format
        self.markup_format_editable = markup_format is None
        self.escape_html = escape_html

        self.markup_choices = markup_choices
        self.markup_choices_list = [mc[0] for mc in markup_choices]
#        self.markup_choices_dict = dict(markup_choices)

        # default_markup_format in markup_choices ?
        if (self.default_markup_format and (self.default_markup_format not in self.markup_choices_list)):
            raise ValueError("Invalid 'default_markup_format' for field '{}', allowed values: {}".format(name, ', '.join(self.markup_choices_list)))

        # for South FakeORM compatibility: the frozen version of a
        # MarkupField can't try to add a _rendered field, because the
        # _rendered field itself is frozen as well. See introspection
        # rules below.
        self.rendered_field = not kwargs.pop('rendered_field', False)

        super(MarkupField, self).__init__(verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        self.rendered_field_name = self.rendered_field_name or _rendered_field_name(name)
        self.markup_format_field_name = _markup_format_field_name(name)

        if not cls._meta.abstract:
#            choices = zip(self.markup_choices_list, self.markup_choices_list)

            markup_format_field = models.CharField(max_length=30, choices=self.markup_choices, default=self.default_markup_format, editable=self.markup_format_editable, blank=self.blank)
            markup_format_field.creation_counter = self.creation_counter - 1
            cls.add_to_class(_markup_format_field_name(name), markup_format_field)

#            self.creation_counter += 1

#            if not self.render_to_field:
            rendered_field = models.TextField(editable=False)
#            rendered_field = models.TextField(editable=True)
            rendered_field.creation_counter = self.creation_counter + 1

            cls.add_to_class(self.rendered_field_name, rendered_field)

        super(MarkupField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, MarkupDescriptor(self))

    def pre_save(self, model_instance, add):
        value = super(MarkupField, self).pre_save(model_instance, add)
        if value.markup_format not in self.markup_choices_list:
            raise ValueError('Invalid markup format (%s), allowed values: %s' %
                             (value.markup_format,
                              ', '.join(self.markup_choices_list)))
        if self.escape_html:
            raw = escape(value.raw)
        else:
            raw = value.raw
#        rendered = self.markup_choices_dict[value.markup_format](raw)
        rendered = settings.MARKUP_FILTERS[value.markup_format](raw)
#        setattr(model_instance, _rendered_field_name(self.attname), rendered)
        setattr(model_instance, self.rendered_field_name, rendered)
        return value.raw

    def get_prep_value(self, value):
        if isinstance(value, Markup):
            return value.raw
        else:
            return value

    # copy get_prep_value to get_db_prep_value if pre-1.2
    if django.VERSION < (1,2):
        get_db_prep_value = get_prep_value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.raw

    def formfield(self, **kwargs):
        defaults = {'widget': widgets.MarkupTextarea}
        defaults.update(kwargs)
        return super(MarkupField, self).formfield(**defaults)

# register MarkupField to use the custom widget in the Admin
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
FORMFIELD_FOR_DBFIELD_DEFAULTS[MarkupField] = {'widget': widgets.AdminMarkupWidget}

# allow South to handle MarkupField smoothly
try:
    from south.modelsinspector import add_introspection_rules
    # For a normal MarkupField, the add_rendered_field attribute is
    # always True, which means no_rendered_field arg will always be
    # True in a frozen MarkupField, which is what we want.
    add_introspection_rules(rules=[
        ( (MarkupField,), [], { 'rendered_field': ['rendered_field', {}], })
    ], patterns=['markitup_field\.fields\.MarkupField'])
except ImportError:
    pass
