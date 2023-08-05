"""Define interfaces for FolderContentsPortletManager.
"""
from plone.portlets.interfaces import IPortletManager
import zope.interface

class IFolderContentsPortletManager(IPortletManager):
    """Portlet manager besides the folder_contents table view
    """

class IFolderContentsPortletManagerInstalled(zope.interface.Interface):
    """A layer specific for this add-on product.

    This interface is referred in browserlayers.xml.

    All views and viewlets register against this layer will appear on your Plone site
    only when the add-on installer has been run.     """