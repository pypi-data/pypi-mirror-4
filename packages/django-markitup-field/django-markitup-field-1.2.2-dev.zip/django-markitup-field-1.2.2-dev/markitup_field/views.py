from django.shortcuts import render_to_response
from django.template import RequestContext

from markitup_field.settings import MARKUP_FILTERS

def apply_filter(request):
    markup = request.POST.get('data', '')
    markup_format = request.POST.get('markup_format', 'text')
    rendered = MARKUP_FILTERS[markup_format](markup)
    return render_to_response('markitup/preview.html',
        {'preview': rendered},
        context_instance=RequestContext(request))
