from zope.interface import implements
import random
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
from zope import schema
from zope.formlib import form
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl import getSecurityManager
from zope.component import getMultiAdapter, getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


# TODO: If you require i18n translation for any of your schema fields below,
# uncomment the following to import your package MessageFactory
from collective.portlet.manualRelated import ManualRelatedPortletMessageFactory as _


class IManualRelatedPortlet(IPortletDataProvider):
    """A portlet that shows collection items

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=False)

    description = schema.TextLine(
        title=_(u"Description"),
        description=_(u"A description to show on top of the portlet followed by a link to the related collection"),
        required=False)
    
    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Specify the maximum number of items to show in the "
                      u"portlet. Leave this blank to show all items."),
        required=False)

    random = schema.Bool(
        title=_(u"Select random items"),
        description=_(u"If enabled, items will be selected randomly from the "
                      u"collection, rather than based on its sort order."),
        required=True,
        default=False)

    show_more = schema.Bool(
        title=_(u"Show more... link"),
        description=_(u"If enabled, a more... link will appear in the footer "
                      u"of the portlet, linking to the underlying "
                      u"Collection."),
        required=True,
        default=True)

    show_dates = schema.Bool(
        title=_(u"Show dates"),
        description=_(u"If enabled, effective dates will be shown underneath "
                      u"the items listed."),
        required=True,
        default=False)
    

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IManualRelatedPortlet)
    
    header = u""
    description = u""
    limit = None
    random = False
    show_more = True
    show_dates = False
    
    def __init__(self, header=u"", description=u"", limit=None, random=False, show_more=True, show_dates=False):
        self.header = header
        self.description = description
        self.limit = limit
        self.random = random
        self.show_more = show_more
        self.show_dates = show_dates
        self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Manual Related Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('manualrelatedportlet.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        
    @property
    def available(self):
        #return True
        return len(self.results())

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-collection-%s" % normalizer.normalize(header)

    def results(self):
        if self.data.random:
            return self._random_results()
        else:
            return self._standard_results()

    def _standard_results(self):
        results = []
        resultlist = []
        collection = self.collection()
        if collection is not None:
            limit = self.data.limit
            if limit and limit > 0:
                # pass on batching hints to the catalog
                results = collection.queryCatalog(batch=True, b_size=limit)
                results = results._sequence
            else:
                results = collection.queryCatalog()
                
            for res in results:
                if res.UID != self.context.UID():
                    resultlist.append(res)
                
            if limit and limit > 0:
                resultlist = resultlist[:limit]
        return resultlist

    def _random_results(self):
        # intentionally non-memoized
        results = []
        resultlist = []
        collection = self.collection()
        if collection is not None:
            results = collection.queryCatalog(sort_on=None)
            if results is None:
                return []
            limit = self.data.limit and min(len(results), self.data.limit) or 1

            for res in results:
                if res.UID != self.context.UID():
                    resultlist.append(res)

            if len(resultlist) < limit:
                limit = len(resultlist)
            resultlist = random.sample(resultlist, limit)

        return resultlist
        
        
    def getTwoWayRelatedContent(self):
        """
        Gets all the manually related content both related items of the current context and items where the current context is marked as related.
        """
        related = []
        related = self.context.getRefs()
        backRelated = self.context.getBRefs()
        
        related.extend(backRelated)
        
        return self._uniq(related);
    
    def _uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]
    
    def collection(self):
        related = self.getTwoWayRelatedContent()
        result = None
        
        for rel in related:
            if rel.portal_type == "Collection" or rel.portal_type == "Topic":
                result = rel
                break
        
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
                
        return result


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IManualRelatedPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IManualRelatedPortlet)
