# -*- coding: utf-8 -*-

from Products.validation import validation

from collective.itvalidators.validators.base_validators import baseValidators

for v in baseValidators:
    validation.register(v)

