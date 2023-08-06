TEST_MAPPING = ['http://nohost/plone|en',
                'http://nohost-fr/plone|fr',
                'http://nohost-nl/plone|nl',
                'http://testhost/plone|en',
                'http://testhost-fr/plone|fr',
                'http://testhost-nl/plone|nl']


class FakeContext:
    def __init__(self):
        self.lang = 'en'

    def Language(self):
        return self.lang


class FakeResponse:
    def __init__(self):
        self.redirect_url = None

    def redirect(self, url):
        self.redirect_url = url


class FakeRequest:
    def __init__(self):
        self.RESPONSE = FakeResponse()
        self._data = {}

    def get(self, key):
        return self._data.get(key)


class FakeSettings:
    def __init__(self):
        self.activated = True
        self.mapping = TEST_MAPPING


class FakeManager:
    def __init__(self, context, request):
        self.portal_url = 'http://nohost/plone'
        self.activated = True
        self.mapping = {'en': 'http://nohost/plone',
                        'fr': 'http://nohost-fr/plone',
                        'nl': 'http://nohost-nl/plone'}
        self.translated_url = {'en': 'http://nohost/plone',
                               'fr': 'http://nohost-fr/plone',
                               'nl': 'http://nohost-nl/plone'}
        self.context = context
        self.request = request

    def get_translated_url(self):
        lang = self.context.Language()
        return self.translated_url.get(lang,
                                       self.request.get('ACTUAL_URL'))
