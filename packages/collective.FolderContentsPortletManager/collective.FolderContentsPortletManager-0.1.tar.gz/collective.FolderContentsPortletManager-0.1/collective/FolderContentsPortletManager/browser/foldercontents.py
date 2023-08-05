from plone.app.content.browser.foldercontents import FolderContentsView as FolderContentsViewOrig
from zope.app.pagetemplate import ViewPageTemplateFile
from AccessControl import getSecurityManager


class FolderContentsView(FolderContentsViewOrig):
    def __init__(self, context, request):
        super(FolderContentsView, self).__init__(context, request)
    
    def showManageButton(self):
        secman = getSecurityManager()
        if not secman.checkPermission('Portlets: Manage portlets', self.context):
            return False
        else:
            return True