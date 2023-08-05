# -*- coding: utf-8 -*-

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Testing.ZopeTestCase import doctest

from Products.validation import validation

class TestValidation(ATSiteTestCase):

    def test_isCAP(self):
        v = validation.validatorFor('isCAP')
        self.failUnlessEqual(v('44021'), 1)
        self.failUnlessEqual(v('00100'), 1)
        self.failUnlessEqual(v('010001'),
                             u"Validation failed(isCAP): '010001' is not a valid CAP.")
        self.failUnlessEqual(v('100'),
                             u"Validation failed(isCAP): '100' is not a valid CAP.")
        self.failUnlessEqual(v('44b50'),
                             u"Validation failed(isCAP): '44b50' is not a valid CAP.")
        self.failUnlessEqual(v('44 21'),
                             u"Validation failed(isCAP): '44 21' is not a valid CAP.")

    def test_isItalianNIN(self):
        v = validation.validatorFor('isItalianNIN')
        self.failUnlessEqual(v('FBBLCU80E24C814Q'), 1)
        # works also lowecase
        self.failUnlessEqual(v('fbblcu80e24c814q'), 1)
        # works also with mized case        
        self.failUnlessEqual(v('FbbLCU80e24C814Q'), 1)

        self.failUnlessEqual(v('FbbLCU80z24C814Q'),
                             u"Validation failed(isItalianNIN): 'FbbLCU80z24C814Q' is not a valid National Insurance Number.")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestValidation))

    doctests = (
        'collective.itvalidators.validators.min_chars',
        'collective.itvalidators.validators.dependency_check',
        )
    for module in doctests:
        suite.addTest(doctest.DocTestSuite(module))

    return suite
