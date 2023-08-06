# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import implements
from agx.testpackage import _
from grokcore.view.components import PageTemplate
from five import grok
from plone.directives import (
    dexterity,
    form,
)

class ICompany(form.Schema):

    name = schema.TextLine(title=_(u"Company Name"),
                           description=_(u"Name of Company"), required=False)
    tax_number = schema.TextLine(title=_(u"Tax Number"),
                                 description=_(u"Tax number of Company"),
                                 required=False)

class CompanyView(dexterity.DisplayForm):

    grok.context(ICompany)
    grok.require('zope2.View')

    template = PageTemplate('templates/company.pt')