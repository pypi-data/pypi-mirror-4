from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.conf import settings

try:
    detect_flavour = settings.DETECT_MOBILE_FLAVOUR
except:
    detect_flavour = False

try:
    disable_helper = settings.DISABLE_MOBILITY_HELPERS
except:
    disable_helper = False

try:
    force_mobile = settings.FORCE_MOBILE
except:
    force_mobile = False


def get_template(request, template_name):
    if disable_helper or not hasattr(request, 'is_mobile'):
        return template_name

    if not request.is_mobile and not force_mobile:
        return template_name

    base, extension = template_name.rsplit('.')
    if detect_flavour and request.mobile_flavour:
        template_name = "%s.%s.%s" % (base, request.mobile_flavour, extension)
    else:
        template_name = "%s.mobile.%s" % (base, extension)

    return template_name


def smart_response(request, template, data):
    return render_to_response(get_template(request, template), data, context_instance=RequestContext(request))
