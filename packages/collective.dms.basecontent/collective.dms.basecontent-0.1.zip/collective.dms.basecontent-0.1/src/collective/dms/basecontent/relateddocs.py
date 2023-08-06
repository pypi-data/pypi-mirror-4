from zope.interface import implements, implementer
from zope.component import adapter, getUtility
from zope.app.intid.interfaces import IIntIds

from zc.relation.interfaces import ICatalog

from z3c.form.interfaces import IFormLayer, IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.schema import RelationChoice, RelationList

from plone.formwidget.contenttree.widget import MultiContentTreeWidget
from plone.formwidget.contenttree import ObjPathSourceBinder

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IRelatedDocs(IRelationList):
    """"""

class RelatedDocsWidget(MultiContentTreeWidget):
    display_template = ViewPageTemplateFile('related-docs-display.pt')
    
    def __init__(self, display_backrefs, request):
        self.display_backrefs = display_backrefs
        super(RelatedDocsWidget, self).__init__(request)

    def get_url(self, v):
        return v

    def get_label(self, v):
        term = self.terms.getTermByToken(v)
        return term.title

    def tuples(self):
        refs = [(self.get_url(x), self.get_label(x)) for x in self.value]
        if self.display_backrefs:
            intids = getUtility(IIntIds)
            catalog = getUtility(ICatalog)
            try:
                doc_intid = intids.getId(self.context)
            except KeyError:
                pass
            else:
                for ref in catalog.findRelations({'to_id': doc_intid}):
                    tp = (ref.from_path, ref.from_object.Title())
                    if tp not in refs:
                        refs.append(tp)
        return refs

@adapter(IRelatedDocs, IFormLayer)
@implementer(IFieldWidget)
def RelatedDocsFieldWidget(field, request):
    return FieldWidget(field, RelatedDocsWidget(field.display_backrefs, request))

class RelatedDocs(RelationList):
    implements(IRelatedDocs)

    def __init__(self, portal_types=None,
                       display_backrefs=False, **kwargs):
        self.display_backrefs = display_backrefs
        kw = dict()
        if portal_types:
            kw['portal_type'] = portal_types
        RelationList.__init__(self,
                        value_type=RelationChoice(
                            title=u'',
                            source=ObjPathSourceBinder(**kw)),
                        **kwargs)

