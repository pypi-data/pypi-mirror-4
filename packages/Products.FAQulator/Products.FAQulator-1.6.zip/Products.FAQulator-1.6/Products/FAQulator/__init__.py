from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
try:
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    from Products.GenericSetup import EXTENSION, profile_registry
    HAS_GENERICSETUP = True
except ImportError:
    HAS_GENERICSETUP = False


from config import *

from zope.i18nmessageid import MessageFactory
FAQulatorMessageFactory = MessageFactory('faqulator')

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    import FAQ, FAQEntry

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

    if HAS_GENERICSETUP:
        profile_registry.registerProfile('FAQulator',
                'FAQulator',
                'Extension profile for default FAQulator setup',
                'profiles/default',
                'FAQulator',
                EXTENSION,
                for_=IPloneSiteRoot)

