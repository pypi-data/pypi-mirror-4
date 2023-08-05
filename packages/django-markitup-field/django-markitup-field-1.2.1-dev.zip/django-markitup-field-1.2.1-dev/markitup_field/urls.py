from django.conf.urls.defaults import url, patterns

from markitup_field.views import apply_filter

urlpatterns = patterns(
    '',
    url(r'^markitup_preview$', apply_filter, name='markitup_preview'),
    )
