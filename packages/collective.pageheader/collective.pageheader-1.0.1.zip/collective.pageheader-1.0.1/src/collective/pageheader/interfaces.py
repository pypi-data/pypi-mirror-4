from zope import interface
from plone.theme.interfaces import IDefaultPloneLayer


class IPageHeaderEnabled(interface.Interface):
    """
    """


class IPageHeaderAvailable(interface.Interface):
    """
    """


class ILayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
