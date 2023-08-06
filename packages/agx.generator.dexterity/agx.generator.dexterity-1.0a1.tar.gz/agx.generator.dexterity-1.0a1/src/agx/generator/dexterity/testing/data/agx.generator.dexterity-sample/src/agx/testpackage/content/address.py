# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import (
    alsoProvides,
    implements,
)
from plone.directives import form
from agx.testpackage import _

class IAddress(form.Schema):

    street = schema.TextLine(title=_(u"Street"), description=_(u"Street"),
                             required=False)
    zip = schema.TextLine(title=_(u"ZIP"), description=_(u"ZIP"),
                          required=False)
    country = schema.TextLine(title=_(u"Country"),
                              description=_(u"Country Name"), required=False)

alsoProvides(IAddress, form.IFormFieldProvider)

class Address(object):

    implements(IAddress)

    def __init__(self, context):
        self.context = context