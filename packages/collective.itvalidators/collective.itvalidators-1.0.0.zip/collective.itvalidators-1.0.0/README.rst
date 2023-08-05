.. contents:: **Table of contents**

Introduction
============

This product add to Plone some additional `validators`__.

__ http://plone.org/documentation/manual/developer-manual/archetypes/fields/validator-reference

Some of theme can be useful only for Italian users or sites targeted on Italy (as many of the default ones
like ``isSSN`` or ``isUSPhoneNumber`` are not useful for non-US sites), other are simply additional validators
that everyone can find useful.

The idea behind the product is simply collect a set of validators that commonly are putted inside other
products, but in this way not easily reusable.

Italian Specific validators
===========================

isCAP
-----

Very similar to the native ``isZipCode`` but this only accept 5 digits values. Formally is
`Codice di Avviamento Postale`__.

__ http://it.wikipedia.org/wiki/Codice_di_avviamento_postale

isItalianNIN
------------

Check if a string is a valid `Italian National Insurance Number`__ ("Codice Fiscale"). The validator only check
the format of the string, not if the string itself is a *real* and existing code.

__ http://it.wikipedia.org/wiki/Codice_fiscale

General purpose validators
==========================

MinCharsValidator
-----------------

This validator test if the given value is at least a specific number of characters long. The default
character value is 500.

The validator will also ignore any whitespace (space character, carriage return, tab...) so the text::

    Hello World

is long like::

    Hello      World

and also long like::

    Hello   
    
         World

How to use
~~~~~~~~~~

An example::

    from collective.itvalidators.validators import MinCharsValidator
    ...
    
    TextField('text',
              validators = (MinCharsValidator()),
    ),
    ...

To customize the number of characters::

    TextField('text',
              validators = (MinCharsValidator(100)),
    ),
    ...

You can also threat is a special way HTML text (for example, if it came from TinyMCE) beeing sure that only
content characters (not HTML tags) are counted. Example::

    ...
    TextField('text',
              default_output_type = 'text/x-html-safe',
              validators = ('isTidyHtmlWithCleanup', MinCharsValidator(100, strict=True)),
    ),
    ...

DependencyCheckValidator
------------------------

This validator check the value ("*wanted value*") contained in a field, but only when another field contains
a "*warning value*".
This mean that when the *observed* field isn't matching the value you are monitor, no validation take place;
when this is true, a second level of validation of the current field take place.

You need to configure this validator giving the ``observed`` field. After that you need to provide both
``warnValue`` and ``wantedValue``.

Example:

    Check that when an observed field contains the value "*Other...*", this field contains the value "*Foo*".

This first example seems not very useful but know that both configuration parameters can be a specific
value, or a boolean value.

When using boolean values:

* When ``warnValue`` is *False* mean that you want to monitor when the *observed* field is empty.
* When ``warnValue`` is *True* mean that you want to monitor when the *observed* field is not empty.
* When ``wantedValue`` is *False* mean that validation will pass if the field if empty.
* When ``wantedValue`` is *True* mean that validation will pass if the field not empty (see below).

Another (better) example:

    Check that when an observed field contains the value "*Other...*", this field contains *something*.

How to use
~~~~~~~~~~

The first example above::

    from collective.itvalidators.validators import DependencyCheckValidator
    ...
    
    StringField('field1',),
    StringField('field2',
                validators = (DependencyCheckValidator('field1', warnValue='Other...', wantedValue='Foo')),
    ),
    ...

The second example above::

    ...
    StringField('field1',),
    StringField('field2',
                validators = (DependencyCheckValidator('field1', warnValue='Other...', wantedValue=True)),
    ),
    ...

Final note
~~~~~~~~~~

Normally Archetypes framework doesn't run validation for non-required empty fields. This happens adding as first validator
a default sufficient "*isEmptyNoError*".

You probably need to play with Products.validation APIs to use ``wantedValue`` True::

    YourSchema['field2'].validators.insertRequired(
                    DependencyCheckValidator('field1', warnValue='Other...', wantedValue=True)
    )

This will add in position 0 a required validator. In this way the validation runs normally.

Contribute!
===========

You are welcome to add to this product your additional validation (also some unit-tests for every new validator
are welcome)! Contact us at sviluppoplone@redturtle.it

You can also contribute providing new translation for validation messages.

Credits
=======

Developed with the support of:

* `Azienda USL Ferrara`__
  
  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL's logo
  
* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg 
     :alt: S. Anna Hospital - logo
   
* `Regione Emilia Romagna`__

All of them supports the `PloneGov initiative`__.

__ http://www.ausl.fe.it/
__ http://www.ospfe.it/
__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

