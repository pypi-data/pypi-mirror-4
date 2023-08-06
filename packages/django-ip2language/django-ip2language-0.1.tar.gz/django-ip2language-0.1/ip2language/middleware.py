from django.http import HttpResponseRedirect

from .locator import iplocator


class LanguagePreferenceMiddleware:
    def process_request(self, request):
        if not request.path == '/':
            return None

        language = iplocator.get_language(request.META['REMOTE_ADDR'])
        return HttpResponseRedirect('/{0}/'.format(language))
