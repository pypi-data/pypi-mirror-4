import unittest
import timemonitor as tm
from time import sleep

class TestTimeMonitor(unittest.TestCase):

    def test_monitor_created(self):
        with tm.TimeMonitor("testtimer"):
            pass
        self.assertTrue(tm._monitors.has_key("testtimer"))

    def test_monitor_incremented(self):
        with tm.TimeMonitor("testtimer"):
            sleep(3)
        self.assertAlmostEqual(tm._monitors["testtimer"], 3, places=2)

    def test_monitor_reset(self):
        with tm.TimeMonitor("testtimer"):
            sleep(3)
        tm.reset()
        self.assertEqual(tm._monitors["testtimer"], 0)

    def test_monitor_accumulated(self):
        with tm.TimeMonitor("testtimer"):
            sleep(3)
        self.assertAlmostEqual(tm._monitors["testtimer"], 3, places=2)
        sleep(2)
        with tm.TimeMonitor("testtimer"):
            sleep(3)
        self.assertAlmostEqual(tm._monitors["testtimer"], 6, places=1)

    def test_summarize(self):
        with tm.TimeMonitor("testtimer"):
            sleep(3)
        printed = tm.summarize()
        self.assertGreater(printed.find("testtimer"), -1) 
        self.assertGreater(printed.find("3"), -1) 

    def tearDown(self):
        tm.reset()
