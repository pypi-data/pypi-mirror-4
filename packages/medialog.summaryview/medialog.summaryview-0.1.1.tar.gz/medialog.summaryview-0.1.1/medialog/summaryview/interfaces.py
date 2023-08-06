from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer
    
class ISummaryHiddenObject(Interface):
    """Marker interface for marking an object to hide is from summaryview"""
    
class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """