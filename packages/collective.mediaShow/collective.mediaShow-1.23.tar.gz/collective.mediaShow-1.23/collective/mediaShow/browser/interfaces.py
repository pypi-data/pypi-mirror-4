from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.interface import implements, Interface


class IMediaShowSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
