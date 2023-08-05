"""
widgets for django-markitup

Time-stamp: <2011-11-26 14:39:52 carljm widgets.py>

"""
import random
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminTextareaWidget
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings

from markitup_field.settings import MARKUP_SKIN, MARKUP_AUTO_PREVIEW, JQUERY_URL
from markitup_field.util import absolute_url
import posixpath

class MarkupInput(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is not None:
            # Special handling for MarkupField value.
            # This won't touch simple TextFields because they don't have
            # 'raw' attribute.
            try:
                value = value.raw
            except AttributeError:
                pass
        return super(MarkupInput, self).render(name, value, attrs)


class MarkupTextarea(MarkupInput, forms.Textarea):
    pass


class MarkupHiddenWidget(MarkupInput, forms.HiddenInput):
    pass


class MarkupWidget(MarkupTextarea):
    """
    Widget for a MarkItUp editor textarea.

    Takes two additional optional keyword arguments:

    ``markitup_set``
        URL path (absolute or relative to STATIC_URL) to MarkItUp
        button set directory.  Default: value of MARKITUP_SET setting.

    ``markitup_skin``
        URL path (absolute or relative to STATIC_URL) to MarkItUp skin
        directory.  Default: value of MARKITUP_SKIN setting.

    """
    def __init__(self, attrs=None, markup_set=None, markup_skin=None, auto_preview=None):

    #        self.miu_set = absolute_url(markup_set or settings.MARKUP_SET)
        self.miu_skin = absolute_url(markup_skin or MARKUP_SKIN)
        if auto_preview is None:
            auto_preview = MARKUP_AUTO_PREVIEW
        self.auto_preview = auto_preview
        #        super(MarkupWidget, self).__init__(attrs)
        super(MarkupWidget, self).__init__({'class': 'dice_markup_editor'})

    #    def _media(self):
    #        js_media = [absolute_url(settings.JQUERY_URL)] if settings.JQUERY_URL is not None else []
    #        js_media = js_media + [absolute_url('markitup/ajax_csrf.js'),
    #                               absolute_url('markitup/jquery.markitup.js'),
    #                               posixpath.join(self.miu_set, 'set.js')]
    #        return forms.Media(css={'screen': (posixpath.join(self.miu_skin, 'style.css'), posixpath.join(self.miu_set, 'style.css'))},
    #                           js=js_media)
    #    media = property(_media)

    def _media(self):
        js = []

        if JQUERY_URL is not None:
            js.append(absolute_url(JQUERY_URL))

        js.append(absolute_url('markitup/ajax_csrf.js'))
        js.append(absolute_url('markitup/jquery.markitup.js'))
        js.append(absolute_url('markitup/update_widget.js'))

        css = []
        css.append(absolute_url(posixpath.join(self.miu_skin, 'style.css')))
        css.append(absolute_url('markitup/sets/style.css'))

        return forms.Media(css={'all': css}, js=js)
    media = property(_media)

#    class Media:
#        css = {'all': (
#            absolute_url('markitup/skins/simple/style.css'),
##            absolute_url(posixpath.join(miu_skin, 'style.css')),
#            absolute_url('markitup/sets/style.css'),
#            )}
#
#        js = (absolute_url('markitup/ajax_csrf.js'),
#              absolute_url('markitup/jquery.markitup.js'),
#              absolute_url('markitup/update_widget.js'),
#            )


    def render(self, name, value, attrs=None):
        html = super(MarkupWidget, self).render(name, value, attrs)

        final_attrs = self.build_attrs(attrs)

        if self.auto_preview:
            auto_preview = "$('a[title=\"Preview\"]').trigger('mouseup');"
        else:
            auto_preview = ''

        try:
            preview_url = (
                'mySettings["previewParserPath"] = "%s";'
                % reverse('markitup_preview'))
        except NoReverseMatch:
            preview_url = ""

        html_script = """
        <script type="text/javascript">
        (function($) {
          $(document).ready(function() {
            var element = $("#%(id)s");
            if(!element.hasClass("markItUpEditor")) {
              %(preview_url)s
              element.markItUp(mySettings);
            }
            %(auto_preview)s
          });
          })(jQuery);
        </script>
        """ % {'id': final_attrs['id'], 'auto_preview': auto_preview, 'preview_url': preview_url,
               'my_settings': '/static/markitup/sets/markdown/set.js'}

        #        html += html_script

        html_script = """<script>
        var STATIC_URL = '{}';
        var MARKITUP_PREVIEW_URL = '{}';
        </script>
        """.format(settings.STATIC_URL, reverse('markitup_preview'))
        html += html_script

        return mark_safe(html)


class AdminMarkupWidget(MarkupWidget, AdminTextareaWidget):
    """
    Add vLargeTextarea class to MarkupWidget so it looks more
    similar to other admin textareas.

    """
    pass


