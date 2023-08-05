from zope import component
from plone.app.layout.viewlets.common import ViewletBase

from collective.linguadomains import interfaces

import logging
logger = logging.getLogger('collective.linguadomains')


class URLValidator(ViewletBase):
    """Viewlet that check language of the content page against translated url
    if the language do not correspond to the content you will be redirected
    to the same page with the corresponding URL
    """
    def __init__(self, context, request, view, manager=None):
        super(URLValidator, self).__init__(context, request, view,
                                           manager=manager)
        self._manager = None

    def index(self):
        """This viewlet check stuff, it doesn't display anythings"""
        return u""

    def language(self):
        return self.context.Language()

    def get_manager(self):
        if self._manager is None:
            self._manager = component.getMultiAdapter((self.context,
                                                       self.request),
                                           interfaces.ILinguaDomainsManager)
        return self._manager

    def update(self):
        request = self.request
        if self.request.get('donotcheck'):
            return

        url = self.request.get('ACTUAL_URL')
        manager = self.get_manager()
        redirect_url = manager.get_translated_url()

        if url == redirect_url:
            return

        request.RESPONSE.redirect(redirect_url)
        logger.info('REDIRECT')
