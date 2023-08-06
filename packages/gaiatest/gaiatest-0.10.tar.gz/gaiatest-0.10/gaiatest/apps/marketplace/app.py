# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.keys import Keys
from gaiatest.apps.base import Base


class Marketplace(Base):

    name = 'Marketplace'

    _marketplace_iframe_locator = ('css selector', 'iframe[src*="marketplace"]')

    _loading_fragment_locator = ('css selector', 'div.loading-fragment')
    _error_title_locator = ('css selector', '#appError-appframe1 h3[data-l10n-id="error-title"]')
    _error_message_locator = ('css selector', '#appError-appframe1 span[data-l10n-id="error-message"]')

    # Marketplace search on home page
    _search_locator = ('id', 'search-q')

    def __init__(self, marionette, app_name=False):
        Base.__init__(self, marionette)
        if app_name:
            self.name = app_name

    def switch_to_marketplace_frame(self):
        """Only Marketplace production has a frame for the app."""
        self.marionette.switch_to_frame(self.marionette.find_element(*self._marketplace_iframe_locator))

    def launch(self):
        Base.launch(self)
        self.wait_for_element_not_displayed(*self._loading_fragment_locator)

    @property
    def error_title_text(self):
        return self.marionette.find_element(*self._error_title_locator).text

    @property
    def error_message_text(self):
        return self.marionette.find_element(*self._error_message_locator).text

    def search(self, term):
        search_box = self.marionette.find_element(*self._search_locator)

        # search for the app
        search_box.send_keys(term)
        search_box.send_keys(Keys.RETURN)
        from gaiatest.apps.marketplace.regions.search_results import SearchResults
        return SearchResults(self.marionette)
