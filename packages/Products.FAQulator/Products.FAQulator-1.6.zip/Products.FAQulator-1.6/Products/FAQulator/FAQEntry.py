from Products.CMFCore import permissions
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.FAQulator.config import *
from Products.FAQulator import FAQulatorMessageFactory as _

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

schema  = ATContentTypeSchema.copy() + Schema((
    TextField("answer",
        required                = True,
        searchable              = True,
        primary                 = True,
        allowable_content_types = ('text/html', 'text/plain'),
        default_content_type    = 'text/html',
        default_output_type     = 'text/html',
        widget                  = RichWidget(
            label       = _(u"faq_answer_label", default=u"Answer"),
            description = _(u"faq_answer", default=u"The answer to the question."),
            )
        ),
    ))

schema['allowDiscussion'].schemata = 'default'
schema.delField('description')

schema["title"].widget=StringWidget(
                label             = _(u"faq_question_label", default=u"Question"),
                description       = _(u"faq_question", default=u"A commonly asked question.")
                )
schema.moveField("answer", after="title")

class FAQEntry(ATCTContent):
    """A frequently asked question."""

#    __implements__             = (ATCTContent.__implements__,)
    schema                     = schema
    global_allow               = False
    _at_rename_after_creation  = True
    archetype_name             = "Question"
    content_icon               = "faq_icon.gif"

    actions = [{ 'id': 'edit',
                 'name': 'Edit',
                 'action': 'string:${object_url}/base_edit',
                 'condition': 'python: not object.get("isCanonical", False) or object.isCanonical()',
                 'permissions': (permissions.ModifyPortalContent,),
                 },
               { 'id': 'translate',
                 'name': 'Edit',
                 'action': 'string:${object_url}/translate_item',
                 'condition': 'python: object.get("isCanonical", False) and not object.isCanonical()',
                 'permissions': (permissions.ModifyPortalContent,),
                 },
               ]

    def getQuestion(self):
        return self.Title()


registerType(FAQEntry, PROJECTNAME)
