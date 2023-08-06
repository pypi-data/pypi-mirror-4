import unittest

from smssluzbacz_api.test import test_transport
from smssluzbacz_api.test.post import test_post_api
from smssluzbacz_api.test.lite import test_lite_api


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromModule(test_transport))
    suite.addTest(loader.loadTestsFromModule(test_post_api))
    suite.addTest(loader.loadTestsFromModule(test_lite_api))
    unittest.TextTestRunner(verbosity=2).run(suite)