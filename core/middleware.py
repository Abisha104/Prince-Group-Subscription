from django.utils import translation
from django.conf import settings


class LanguageMiddleware:
    """Middleware to handle language preference from session/cookie"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for language in session or cookie
        lang = request.session.get('language')
        if not lang:
            lang = request.COOKIES.get('language')

        if lang and lang in ['en', 'ta']:
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        else:
            translation.activate(settings.LANGUAGE_CODE)

        response = self.get_response(request)

        # Set language cookie
        if hasattr(request, 'LANGUAGE_CODE'):
            response.set_cookie('language', request.LANGUAGE_CODE, max_age=31536000)

        return response