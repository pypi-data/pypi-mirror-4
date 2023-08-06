# -*- coding: utf-8 -*-
from zope.interface import implements
from agx.testpackage.interfaces import IUtilityInterface

class SomeUtility(object):

    implements(IUtilityInterface)

class NamedUtility(object):

    implements(IUtilityInterface)