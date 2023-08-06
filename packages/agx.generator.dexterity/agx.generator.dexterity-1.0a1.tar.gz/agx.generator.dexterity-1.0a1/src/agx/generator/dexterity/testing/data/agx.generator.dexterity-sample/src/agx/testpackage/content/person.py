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

class IPerson(form.Schema):

    name = schema.TextLine(title=_(u"First Name"),
                           description=_(u"First name of person"),
                           required=False)
    lastname = schema.TextLine(title=_(u"Last Name"),
                               description=_(u"Last Name of Person"),
                               required=False)
    age = schema.Int(title=_(u"Age"), description=_(u"Age of Person"),
                     required=False)

class PersonView(dexterity.DisplayForm):

    grok.context(IPerson)
    grok.require('zope2.View')

    template = PageTemplate('templates/person.pt')