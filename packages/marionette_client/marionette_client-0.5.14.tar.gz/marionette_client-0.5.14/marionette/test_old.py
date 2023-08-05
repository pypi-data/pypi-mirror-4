import os
from marionette_test import MarionetteTestCase
from errors import JavascriptException, MarionetteException

class TestMarionetteJSCmd(MarionetteTestCase):
    pass
#class TestMarionetteJSCmdChrome(TestMarionetteJSCmd):
class TestMarionetteJSCmdChrome(MarionetteTestCase):
    def setUp(self):
        MarionetteTestCase.setUp(self)
        self.marionette.set_context("chrome")

    def test_marionette_cmd(self):
        self.marionette.set_script_timeout(10000)
        result = self.marionette.execute_script("""
        runMarionetteCmd("log", ["asdf", "DEB"], null);
        return runMarionetteCmd("get_logs", null, null);
        """);
        print result
        self.assertTrue("asdf" in result[-1])
        result = self.marionette.execute_script("""
        return runMarionetteCmd("execute_script", "return 1+4", null);
        """);
        print result

    def tearDown(self):
        self.marionette.set_context("content")
        MarionetteTestCase.tearDown(self)

