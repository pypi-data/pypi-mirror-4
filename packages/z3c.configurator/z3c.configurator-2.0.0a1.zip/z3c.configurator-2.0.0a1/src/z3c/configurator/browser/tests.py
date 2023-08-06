import unittest

try:
    from zope.app.testing import functional
    HAVE_FTEST = True
except ImportError:
    HAVE_FTEST = False

TestLayer = None
if HAVE_FTEST:
    functional.defineLayer('TestLayer', 'ftesting.zcml')


def setUp(test):
    """Setup a reasonable environment for the category tests"""
    pass


def tearDown(test):
    pass


def test_suite():
    suite = unittest.TestSuite()
    if HAVE_FTEST:
        suites = (
            functional.FunctionalDocFileSuite(
                'README.txt', setUp=setUp, tearDown=tearDown,
                ),
            )
        for s in suites:
            s.layer=TestLayer
            suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
