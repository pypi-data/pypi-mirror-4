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

class IDepartment(form.Schema):

    name = schema.TextLine(title=_(u"Department Name"),
                           description=_(u"Name of Department"),
                           required=False)

class DepartmentView(dexterity.DisplayForm):

    grok.context(IDepartment)
    grok.require('zope2.View')

    template = PageTemplate('templates/department.pt')