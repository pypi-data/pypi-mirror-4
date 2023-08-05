# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import time
from marionette_test import MarionetteTestCase

class TestClick(MarionetteTestCase):
    def test_click(self):
        time.sleep(2)
        self.marionette.navigate("file:///data/local/demo.html")
        link = self.marionette.find_element("id", "mozLink")
        time.sleep(3)
        link.click()
        self.assertEqual("Clicked", self.marionette.execute_script("return document.getElementById('mozLink').innerHTML;"))
        time.sleep(2)
        input = self.marionette.find_element("id", "demoBox")
        input.send_keys("Marionette is typing this")
        time.sleep(5)
