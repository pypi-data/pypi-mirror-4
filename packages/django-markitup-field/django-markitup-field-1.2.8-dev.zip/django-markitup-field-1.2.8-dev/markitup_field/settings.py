
from django.conf import settings

from markitup_field.markup import MARKUP_FILTERS


MARKUP_FILTERS.update(getattr(settings, 'MARKUP_FILTERS', {}))
MARKUP_CHOICES = getattr(settings, 'MARKUP_CHOICES', None)

if not MARKUP_CHOICES:
    MARKUP_CHOICES = (
        ('text', 'Text'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('textile', 'Textile'),
        ('restructuredtext', 'ReStructured Text'),
        )

    MARKUP_CHOICES = [markup for markup in MARKUP_CHOICES if markup[0] in MARKUP_FILTERS.keys()]

MARKUP_DEFAULT_FORMAT = getattr(settings, 'MARKUP_DEFAULT_FORMAT', 'default')

MARKUP_AUTO_PREVIEW = getattr(settings, 'MARKUP_AUTO_PREVIEW', False)

MARKUP_SKIN = getattr(settings, 'MARKUP_SKIN', 'markitup/skins/simple')

JQUERY_URL = getattr(settings, 'JQUERY_URL', 'http://ajax.googleapis.com/ajax/libs/jquery/1.6/jquery.min.js')

