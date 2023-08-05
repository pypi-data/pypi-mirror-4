from Products.CMFCore.DirectoryView import registerDirectory
GLOBALS = globals()
registerDirectory('skins', GLOBALS)

from zope.i18nmessageid import MessageFactory
PloneboardPortletMessageFactory = MessageFactory('Products.PloneboardPortlet')

