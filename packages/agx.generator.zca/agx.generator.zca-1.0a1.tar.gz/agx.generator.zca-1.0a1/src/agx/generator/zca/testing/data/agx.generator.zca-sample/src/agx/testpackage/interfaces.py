# -*- coding: utf-8 -*-
from zope.interface import Interface

class ISomeInterface(Interface):
    pass

class ISomeBaseInterface(Interface):
    pass

class IAdapted(ISomeBaseInterface):
    pass

class IFunctionAdapted(Interface):
    pass

class IFunctionAdapter(Interface):
    pass

class IUtilityInterface(Interface):
    pass