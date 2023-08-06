try:
    from Products.LinguaPlone.public import process_types, listTypes
    HAS_LINGUAPLONE=True
except ImportError:
    from Products.Archetypes.public import *

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    import MenuNavigation

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from zope.i18nmessageid import MessageIDFactory as MessageFactory

#WebshopMessageFactory = MessageFactory('Products.Webshop')
MenuMessageFactory = MessageFactory('Products.MenuNavigation')
