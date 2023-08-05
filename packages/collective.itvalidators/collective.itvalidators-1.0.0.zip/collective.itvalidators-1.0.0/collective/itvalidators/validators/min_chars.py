# -*- coding: utf-8 -*-

import re

from Products.validation.i18n import recursiveTranslate
from Products.validation.interfaces.IValidator import IValidator
from Products.CMFCore.utils import getToolByName

from collective.itvalidators import validatorsMessageFactory as _
from zope.i18nmessageid import Message

from zope.interface import implements
import sys

class MinCharsValidator:
    """
    Validator for having a minimum number of characters in a text

    The simplest usage ask you a number of characters

    >>> val = MinCharsValidator(10, strict=False) 
    >>> class D: text='Hello World'
    >>> d = D()
    >>> val(d.text, d) is True
    True

    now lets fail a test
    >>> d.text = 'Hello'
    >>> val(d.text, d)
    u'Required min 10 chars, provided 5'

    It is also possible to specify the error string

    >>> val=MinCharsValidator(20, strict=False, errormsg='you provided only %(current)s characters') 
    >>> val(d.text, d)
    'you provided only 5 characters'

    """

    if sys.version_info[:2] >= (2, 6):
        implements(IValidator)
    else:
        __implements__ = (IValidator,)

    name = 'mincharsvalidator'

    def __init__(self, chars=500, strict=False, errormsg=None):
        self.chars=chars
        self.strict=strict
        self.errormsg=errormsg

    def __call__(self, value, instance, *args, **kwargs):
        
        kw={
           'here':instance,
           'object':instance,
           'instance':instance,
           'value':value,
           'chars':self.chars,
           'args':args,
           'kwargs':kwargs,
           }
        
        # get text
        if not self.strict:
            text = value 
        else:
            ttool = getToolByName(instance, 'portal_transforms')
            text = ttool.convertToData('text/plain', value)
        
        # \xc2\xa0 seems used widely by TinyMCE...
        stripped = re.sub(r'(\s|\xc2\xa0)', '', text)
        
        if len(stripped)>=self.chars:
            return True
        
        kw['current'] = len(stripped)
                
        if self.errormsg and type(self.errormsg) == Message:
            #hack to support including values in i18n message, too. hopefully this works out
            #potentially it could unintentionally overwrite already present values
            #self.errormsg.mapping = kw
            if self.errormsg.mapping:
                self.errormsg.mapping.update(**kw)
            return recursiveTranslate(self.errormsg, **kwargs)
        elif self.errormsg:
            # support strings as errormsg for backward compatibility
            return self.errormsg % kw
        else:
            msg = _('min_chars_error_msg',
                    default=u'Required min $chars chars, provided ${current}',
                    mapping={'chars': self.chars, 'current': len(stripped)})
            return recursiveTranslate(msg, **kwargs)
