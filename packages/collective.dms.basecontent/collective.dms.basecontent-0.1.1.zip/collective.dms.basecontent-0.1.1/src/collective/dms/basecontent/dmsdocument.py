from zope import schema
from zope.interface import implements
from zope.component import queryUtility
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy

from plone.supermodel import model
from five import grok
from collective.dms.basecontent.relateddocs import RelatedDocs

from . import _
from ._field import LocalRolesToPrincipals

from zope.schema.interfaces import IVocabularyFactory


class IDmsDocument(model.Schema):
    """ """

    notes = schema.Text(
        title=_(u"Notes"),
        required=False,
        )

    treating_groups = LocalRolesToPrincipals(
        title=_(u"Treating groups"),
        required=False,
        roles_to_assign=('Editor',),
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.treating_groups',)
        )

    recipient_groups = LocalRolesToPrincipals(
        title=_(u"Recipient groups"),
        required=False,
        roles_to_assign=('Reader',),
        value_type=schema.Choice(vocabulary=u'collective.dms.basecontent.recipient_groups',)
        )

    related_docs = RelatedDocs(
        title=_(u"Related documents"),
        required=False,
        display_backrefs=True)



class DmsDocument(Container):
    """ """

    implements(IDmsDocument)


class DmsDocumentSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IDmsDocument, )


class TreatingGroupsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        standard_groups = queryUtility(IVocabularyFactory, name=u'plone.app.vocabularies.Groups')
        return standard_groups.__call__(context)

grok.global_utility(TreatingGroupsVocabulary, name=u"collective.dms.basecontent.treating_groups")


class RecipientGroupsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        standard_groups = queryUtility(IVocabularyFactory, name=u'plone.app.vocabularies.Groups')
        return standard_groups.__call__(context)

grok.global_utility(RecipientGroupsVocabulary, name=u"collective.dms.basecontent.recipient_groups")
