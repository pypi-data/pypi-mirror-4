# -*- coding: utf-8 -*-

from Products.validation.i18n import recursiveTranslate
from Products.validation.interfaces.IValidator import IValidator
from Products.CMFCore.utils import getToolByName

from collective.itvalidators import validatorsMessageFactory as _
from zope.i18nmessageid import Message

from zope.interface import implements
import sys

class DependencyCheckValidator:
    """ 
    Validator for making a field required when another field is not giving a proper value.

    >>> class W:
    ...     label = "Main text"
    ...
    >>> class F:
    ...     widget = W()
    ...
    >>> class D:
    ...     text = None
    ...     def getField(self, id):
    ...         return F()
    ...
    >>> class Request:
    ...     form = {}
    ...
    >>> request = Request()

    Check that an "observed" field value is "warnValue" or not. Test pass is this is False. Think this value as a
    dangerous value: we need to stop validation (or take additional choices) if this value is found in the "observed"
    field:

    >>> request.form = {'text': 'Good value'}
    >>> d = D()
    >>> d.text = 'Foo'
    >>> val = DependencyCheckValidator('text', warnValue='Warning!', wantedValue='Ignored')
    >>> val(d.text, d, REQUEST=request)
    True

    In this case the "wantedValue" is totally ignored, as the "warnValue" check did not match.

    If the "observed" field match the "warnValue", check also that the validation field value is "wantedValue".
    If this is true, validation still pass:

    >>> request.form = {'text': 'Warning!'}
    >>> d = D()
    >>> d.text = "Foo"
    >>> val = DependencyCheckValidator('text', warnValue='Warning!', wantedValue='Foo')
    >>> val(d.text, d, REQUEST=request)
    True

    But validation will not pass if the "wantedValue" will not match:
    
    >>> d.text = "Unwanted value"
    >>> val = DependencyCheckValidator('text', warnValue='Warning!', wantedValue='Foo')
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is "Warning!". This requires that this field contains "Foo".'

    You can use a boolean False as "warnValue" if you need to check that "observed" field
    doesn't contains any value: False "warnValue" mean you want to validate current field when
    "observed" field is empty:

    >>> val = DependencyCheckValidator('text', warnValue=False, wantedValue='Foo')
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {'text': ''}
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is empy. This requires that this field contains "Foo".'

    If current field match "wantedValue", validation still pass:
    
    >>> d.text = 'Foo'
    >>> val(d.text, d, REQUEST=request)
    True

    You can use a boolean True as "warnValue" if you need to check that "observed" field
    is not empty: True "warnValue" mean you want to validate current field when "observed"
    field contains a (any) value:

    >>> d.text = ""
    >>> request.form = {'text': ''}
    >>> val = DependencyCheckValidator('text', warnValue=True, wantedValue='Foo')
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {'text': 'Whatever text'}
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is not empty. This requires that this field contains "Foo".'

    If current field match "wantedValue", validation still pass:

    >>> d.text = 'Foo'
    >>> val(d.text, d, REQUEST=request)
    True

    We can also use boolean values for the "wantedValue" parameter. The meaning is someway similar.
    
    If we use a True value as "wantedValue", validation will pass if the current field is not empty:

    >>> d.text = 'Any'
    >>> request.form = {'text': 'Warning!'}
    >>> val = DependencyCheckValidator('text', warnValue="Warning!", wantedValue=True)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = ''
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is "Warning!". This requires that this field contains a value.'

    On the other hand, a False "wantedValue" needs that the current field is empty:

    >>> val = DependencyCheckValidator('text', warnValue="Warning!", wantedValue=False)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = 'Any'
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is "Warning!". This requires that this field contains no value.'

    We can of course mix boolean values for "warnValue" and "wantedValue".

    You can check if "observed" field contains a value. If not: being sure that this field contains
    a value:

    >>> request.form = {'text': 'Any'}
    >>> val = DependencyCheckValidator('text', warnValue=False, wantedValue=True)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {}    
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = ''
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is empy. This requires that this field contains a value.'

    You can check if "observed" field contains a value. If not: being sure that this field doesn't
    contains any value:

    >>> request.form = {'text': 'Any'}
    >>> val = DependencyCheckValidator('text', warnValue=False, wantedValue=False)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {}    
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = 'Bad'
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is empy. This requires that this field contains no value.'

    You can check if "observed" field contains no value. But if it contains a value, being sure that
    this field contains no value:

    >>> d.text = ''
    >>> request.form = {'text': ''}
    >>> val = DependencyCheckValidator('text', warnValue=True, wantedValue=False)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {'text': 'Any'}
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = 'Wrong!'
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is not empty. This requires that this field contains no value.'

    You can check if "observed" field contains no value. But if it contains a value, being sure that
    also this field contains something:

    >>> d.text = 'Any'
    >>> request.form = {'text': ''}
    >>> val = DependencyCheckValidator('text', warnValue=True, wantedValue=True)
    >>> val(d.text, d, REQUEST=request)
    True
    >>> request.form = {'text': 'Warning!'}
    >>> val(d.text, d, REQUEST=request)
    True
    >>> d.text = ''
    >>> val(d.text, d, REQUEST=request)
    u'"Main text" field value is not empty. This requires that this field contains a value.'

    """
    if sys.version_info[:2] >= (2, 6):
        implements(IValidator)
    else:
        __implements__ = (IValidator,)
        
    name = 'dependencycheckvalidator'

    def __init__(self, observed, warnValue, wantedValue, errormsg=None):
        self.observed = observed
        self.warnValue = warnValue
        self.wantedValue = wantedValue
        self.errormsg = errormsg

    def __call__(self, value, instance, *args, **kwargs):
        
        kw={
           'here': instance,
           'object': instance,
           'instance': instance,
           'value': value,
           'observed': self.observed,
           'warnValue': self.warnValue,
           'wantedValue': self.wantedValue,
           'kwargs': kwargs,
           }
        
        form = kwargs['REQUEST'].form
        
        # *** Checking warnValue ***
        if type(self.warnValue)!=bool:
            # Warn value is a specific value
            if form.get(self.observed)!=self.warnValue:
                return True
            kw['warnValue'] = '"%s"' % self.warnValue
        else: # boolean values
            if self.warnValue:
                if not form.get(self.observed):
                    return True
                kw['warnValue'] = _(u'not empty')
            else:
                if form.get(self.observed):
                    return True
                kw['warnValue'] = _(u'empy')

        # *** Checking wantedValue ***
        if type(self.wantedValue)!=bool:
            if value==self.wantedValue:
                return True
            kw['wantedValue'] = '"%s"' % self.wantedValue
        elif self.wantedValue:
            if value and self.eval_DataGridTrueValue(value):
                return True
            kw['wantedValue'] = _(u"a value")
        else:
            if not value and not self.eval_DataGridTrueValue(value):
                return True
            kw['wantedValue'] = _(u"no value")

        # We are here only when validation fails
        kw['observed'] = instance.getField(self.observed).widget.label
                
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
            msg = _('dependency_check_error_msg',
                    default=u'"$observed" field value is $warnValue. This requires that this field contains $wantedValue.',
                    mapping={'observed': kw['observed'], 'warnValue': kw['warnValue'],
                             'wantedValue': kw['wantedValue']})
            return recursiveTranslate(msg, **kwargs)

    @classmethod
    def eval_DataGridTrueValue(cls, value):
        """
        DataGridField specific True/False checker - something like this is False!
        [{'column_a': '', 'orderindex_': 'template_row_marker', 'column_b': ''}]

        Normal values are evalutated as normal
        
        >>> eval_DataGridTrueValue = DependencyCheckValidator.eval_DataGridTrueValue
        >>> eval_DataGridTrueValue(None)
        False
        >>> eval_DataGridTrueValue(1)
        True
        >>> eval_DataGridTrueValue(0)
        False

        >>> val = [{'column_a': '', 'orderindex_': 'template_row_marker', 'column_b': ''}]
        >>> eval_DataGridTrueValue(val)
        False
        >>> val[0]['column_a'] = 'something'
        >>> eval_DataGridTrueValue(val)
        True
        
        """
        if type(value)==list and len(value)==1:
            elem = value[0]
            if type(elem)==dict or hasattr(elem, 'orderindex_'):
                # ok, is a DataGridfield with one single row. Check if is empty
                for cname, cvalue in elem.items():
                    if cname=='orderindex_':
                        continue
                    if cvalue:
                        return True
                return False
        # In ant other case, normal python meaning is ok
        return bool(value)
