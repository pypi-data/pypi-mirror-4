from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import TextField, BooleanField
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import OrderedBaseFolder, registerType
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.ATContentTypes.configuration import zconf
from config import PROJECTNAME
import AccessControl

schema = BaseSchema.copy() + Schema((
        TextField('text',
                  required=True,
                  searchable=True,
                  primary=True,
                  default_content_type = zconf.ATDocument.default_content_type,
                  default_output_type = 'text/x-html',
                  allowable_content_types = zconf.ATDocument.allowed_content_types,
                  widget = RichWidget(label="Content", allow_file_upload=zconf.ATDocument.allow_document_upload)
                  ),
        BooleanField('excludeFromNav', default=True)
        ))
schema["title"].required = False
schema["title"].widget.visible["edit"] = "invisible"
schema["title"].widget.visible["view"] = "invisible"
schema["title"].default = "Menu HTML-description"

class MenuPage(OrderedBaseFolder):
    """
    """
    schema = schema
    filter_content_types = 1
    allowed_content_types = []
    meta_type = archetype_name = "MenuPage"
    global_allow = 1
    security = AccessControl.ClassSecurityInfo()
    actions = ()

registerType(MenuPage, PROJECTNAME)
