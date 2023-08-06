import unittest

from zope.pagetemplate.tests import test_htmltests as reference


def test_suite():
    return unittest.makeSuite(HTMLTests)


class HTMLTests(reference.HTMLTests):
    def setUp(self):
        import z3c.ptcompat
        import zope.component.testing
        import zope.configuration.xmlconfig
        zope.component.testing.setUp(self)
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', z3c.ptcompat)()

        super(HTMLTests, self).setUp()


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
