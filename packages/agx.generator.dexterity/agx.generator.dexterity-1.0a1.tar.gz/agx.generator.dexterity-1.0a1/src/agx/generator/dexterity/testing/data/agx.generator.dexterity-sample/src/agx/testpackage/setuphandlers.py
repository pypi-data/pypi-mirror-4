# -*- coding: utf-8 -*-
def install(context):
    if context.readDataFile('agx.testpackage_marker.txt') is None:
        return
    portal = context.getSite()