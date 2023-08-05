# -*- coding: utf-8 -*-

from Products.validation.validators.RegexValidator import RegexValidator

from collective.itvalidators import validatorsMessageFactory as _

baseValidators = [

            RegexValidator('isCAP',
                   r'^\d{5}$',
                   title='CAP', description='',
                   errmsg=_(u'is not a valid CAP.')),

            RegexValidator('isItalianNIN',
                   r'^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]\d\d[a-eA-EhHlmLMpPr-tR-T]\d\d[a-zA-Z]\d\d\d[a-zA-Z]$',
                   title='Codice fiscale', description='',
                   errmsg=_(u'is not a valid National Insurance Number.')),
                 
                ]