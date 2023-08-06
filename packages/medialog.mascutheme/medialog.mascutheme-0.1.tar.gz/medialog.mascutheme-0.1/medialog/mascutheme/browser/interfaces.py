from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.portlets.interfaces import IColumn

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Mascutheme Theme" theme, this interface must be its layer
       (in mascutheme/viewlets/configure.zcml).
    """
    
class IMascuthemeTopContent(IColumn):
    """we need our own portlet manager in the top area.
    """