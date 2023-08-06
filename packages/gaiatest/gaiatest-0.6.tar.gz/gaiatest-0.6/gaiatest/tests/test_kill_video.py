from gaiatest import GaiaTestCase


class TestKillVideoPlayer(GaiaTestCase):

    _video_items_locator = ('css selector', 'ul#thumbnails li[data-name]')
    _video_frame_locator = ('id', 'videoFrame')
    _video_loaded_locator = ('css selector', 'video[style]')

    def test_kill_video_app(self):
        self.push_resource('VID_0001.3gp', 'DCIM/100MZLLA')
        self.app = self.apps.launch('Video')
        self.wait_for_element_displayed(*self._video_items_locator)
        self.marionette.tap(self.marionette.find_element(*self._video_items_locator))
        self.wait_for_element_displayed(*self._video_frame_locator)
        self.wait_for_element_displayed(*self._video_loaded_locator)
        self.assertTrue(self.marionette.execute_script("return window.wrappedJSObject.playing;"))
        self.apps.kill(self.app)
