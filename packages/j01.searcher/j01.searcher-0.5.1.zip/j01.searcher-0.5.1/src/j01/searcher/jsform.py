##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema
import zope.i18n
import zope.i18nmessageid

from zope.location import location
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from z3c.form.interfaces import IWidgets
from z3c.form import field
from z3c.form import form

from m01.searcher import criterion
from m01.searcher import filter
from m01.searcher.interfaces import ISearchSession
from m01.searcher.interfaces import ISearchCriterion
from m01.searcher.interfaces import ISearchCriterionWithConnector
from m01.searcher.interfaces import ISearchFilter

from j01.jsonrpc.jsbutton import JSONRPCButton
from j01.jsonrpc import jsform
from j01.jsonrpc import jspage

from j01.dialog.jsform import DialogForm
from j01.dialog.jsbutton import DialogButton
from j01.dialog.jsbutton import DialogCloseButton

from j01.searcher import jsbutton
from j01.searcher import jswidget
from j01.searcher import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


FILTER_NAME_RADIO = """<div class="option">
  <input id="%s" name="filterName" class="searchFilterNameRadio" title="%s" value="%s" type="radio" />
  <label for="%s">
    <span class="label">%s</span>
  </label>
</div>
"""
def renderRadio(key, name):
    """Render a radio option"""
    id = 'filterName-%s' % key
    return FILTER_NAME_RADIO % (id, name, key, id, name)


class IRequiredFilterName(zope.interface.Interface):
    """Required filter name"""

    # filter name used if added to SearchFilterStorage
    name = zope.schema.TextLine(
        title=_(u'Filter Name'),
        description=_(u'Filter Name'),
        missing_value=u'',
        default=u'',
        required=True)


class IFilterDialogButtons(zope.interface.Interface):
    """Filter dialog buttons"""

    save = DialogButton(
        title=_(u'save')
        )

    load = DialogButton(
        title=_(u'load')
        )

    remove = DialogButton(
        title=_(u'remove')
        )

    close = DialogCloseButton(
        title=_(u'close')
        )


class FilterSaveDialog(DialogForm):
    """Filter save dialog for J01SearchForm"""

    ignoreContext = True

    fields = field.Fields(IRequiredFilterName).select('name')

    @property
    def j01DialogTitle(self):
        return zope.i18n.translate(_('Save Filter'), context=self.request)

    def doHandleSaveFilter(self, data):
        # Note we, use the data from the request.form
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # get filter from session
        name = data['name']
        # add filter, our context knows how
        key = self.context.addSearchFilter(name)
        # mark only as finished if we get the new object
        self.nextURL = self.context.pageURL
        self._finishedAdd = True
        self.closeDialog = True
        return key

    @jsform.jsonRPCButtonHandler(IFilterDialogButtons['save'])
    def handleSaveFilter(self, data):
        # Note we, use the data from the request.form
        self.doHandleSaveFilter(data)

    @jsform.jsonRPCButtonHandler(IFilterDialogButtons['close'])
    def handleLoadFilter(self, data):
        # close with javascript
        pass


class FilterLoadDialog(DialogForm):
    """Filter load dialog for J01SearchForm"""

    ignoreContext = True
    removedFilterName = None

    @property
    def j01DialogTitle(self):
        return zope.i18n.translate(_('Load Filter'), context=self.request)

    @property
    def filters(self):
        for data in self.context.getSearchFilterData():
            if self.removedFilterName != data['__name__']:
                # skip removed filter (we didn't commit our transaction yet)
                yield renderRadio(data['__name__'], data['name'])

    def doHandleLoadFilter(self, data):
        key = self.request.form.get('filterName')
        if key is None:
            self.status = _(u'No filter selected')
        else:
            self.context.loadSearchFilter(key)
            self.nextURL = self.context.pageURL
            self.closeDialog = True

    def doHandleRemoveFilter(self, data):
        key = self.request.form.get('filterName')
        if key is None:
            self.status = _(u'No filter selected')
        else:
            if self.context.removeSearchFilter(key):
                self.removedFilterName = key
                self.status = _(u'Selected filter removed')
            else:
                self.status = _(u'Filter not removed')

    @jsform.jsonRPCButtonHandler(IFilterDialogButtons['load'])
    def handleLoadFilter(self, data):
        self.doHandleLoadFilter(data)

    @jsform.jsonRPCButtonHandler(IFilterDialogButtons['remove'])
    def handleLoadFilter(self, data):
        self.doHandleRemoveFilter(data)

    @jsform.jsonRPCButtonHandler(IFilterDialogButtons['close'])
    def handleLoadFilter(self, data):
        # close with javascript
        pass


class IJ01SearcherButtons(zope.interface.Interface):
    """J01SearcherButtons"""

    addCriterion = JSONRPCButton(
        title=_(u'Add'),
        urlGetter=lambda form: form.addCriterionActionURL
        )

    removeCriterion = jsbutton.CriterumFormButton(
        title=_(u'Remove')
        )

    searchByFilter = JSONRPCButton(
        title=_(u'Search'),
        urlGetter=lambda form: form.searchByFilterActionURL
        )

    clearFilter = JSONRPCButton(
        title=_(u'Clear'),
        urlGetter=lambda form: form.clearFilterActionURL
        )

#SAVE_FILTER_JAVASCRIPT = """
#<script type="text/javascript">
#$('#saveFilterFormAdHocLink').click(function(event){
#    j01Dialog({'url': '%s');
#    return false;
#});
#</script>
#"""


class J01CriterionFormBase(jsform.JSONRPCForm):
    """J01 criterion base form"""

    zope.interface.implements(interfaces.IJ01CriterionForm)

    searchForm = None
    searchPage = None

    callback = 'j01RenderContent'

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.update()

    @property
    def prefix(self):
        return '%s.criterion.%s' % (self.searchForm.prefix,
            str(self.criterionName))

    @property
    def removeCriterionID(self):
        return '%s-remove' % self.prefix.replace('.', '-')

    @property
    def removeCriterionLabel(self):
        return zope.i18n.translate(_('[remove]'))

    @property
    def criterionName(self):
        return self.context.__name__

    @property
    def total(self):
        if isinstance(self.context.total, int):
            if self.context.total == 0:
                msg = _(u'0 item')
            elif self.context.total == 1:
                msg = _(u'1 item')
            else:
                msg = _(u'${total} items', mapping={'total': self.context.total})
            return zope.i18n.translate(msg, context=self.request)

    def save(self):
        data, errors = self.widgets.extract()
        if errors:
            self.status = self.formErrorsMessage
            return
        content = self.getContent()
        changed = form.applyChanges(self, content, data)
        if changed:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
        return changed

    def removeJavaScript(self):
        formId = self.searchForm.id.replace('.', '\\\.')
        removeCriterionName = self.searchPage.removeCriterionName
        return """
            $('#%s').on('click', '#%s', function(){
                var data = $('#%s').j01FormToArray('removeCriterion');
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01FormProcessor', %s);
                data['%s'] = '%s';
                proxy.j01FormProcessor(data);
                return false;
            });
            """ % (formId, self.removeCriterionID, formId,
                   self.searchForm.removeCriterionURL, self.callback,
                   removeCriterionName, self.criterionName)


class J01CriterionForm(J01CriterionFormBase):
    """J01 criterion form"""

    fields = field.Fields(ISearchCriterion).select('value')


class J01CriterionWithConnectorForm(J01CriterionFormBase):
    """J01 criterion connector form"""

    fields = field.Fields(ISearchCriterionWithConnector).select(
        'connector', 'value')
    fields['connector'].widgetFactory = jswidget.getConnectorWidget


class J01SearchFormMixin(object):
    """J01SearchForm mixin"""

    filterTemplate = getPageTemplate('filter')

    # default form vars
    prefix = 'form'

    searchForm = None # self is used if None

    criterionRows = []
    rowName = 'j01CriterionForm'

    # caching is important or we will get a new filter each time from session
    _searchFilter = None

    showFilter = True
    showFilterActions = False
    filterStatus = None

    # The filterName is used in the ISearchSession to identify filter
    filterName = 'searchFilter'

    # will probably get overriden by the parent form
    filterFactory = filter.SearchFilter

    def publishTraverse(self, request, name):
        """Allows to traverse to save and load dialog"""
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None:
            raise NotFound(self, name, request)
        return view

    @property
    def selectedFilterName(self):
        msg = zope.i18n.translate(_(u'Filter'))
        if self.searchFilter.name:
            return '%s: %s' % (msg, self.searchFilter.name)
        else:
            return msg

    @property
    def saveFilterDialogURL(self):
        return '%s/saveFilterDialog' % self.pageURL

    @property
    def loadFilterDialogURL(self):
        return '%s/loadFilterDialog' % self.pageURL

#    @property
#    def saveFilterJavaScript(self):
#        formId = self.id.replace('.', '\\\.')
#        return SAVE_FILTER_JAVASCRIPT % '%s?j01FormHandlerName=saveFilter' % (
#            self.pageURL)

    @property
    def addCriterionName(self):
        return '%s.addCriterion' % self.prefix

    @property
    def removeCriterionName(self):
        return '%s.removeCriterion' % self.prefix

    @property
    def availableCriterionFactories(self):
        for name, factory in self.searchFilter.availableCriterionFactories:
            yield {'name': name, 'title': factory.title}

    def createSearchFilter(self):
        """Create SearchFilter"""
        # locate filter, so that security does not get lost
        context = removeSecurityProxy(self.context)
        return self.filterFactory({'__parent__': context})

    @property
    def searchSession(self):
        return ISearchSession(self.request)

    @property
    def searchFilter(self):
        if self._searchFilter is None:
            searchFilter = self.searchSession.getFilter(self.filterName)
            if searchFilter is None:
                searchFilter = self.createSearchFilter()
            self._searchFilter = searchFilter
            self.saveFilter()
        return self._searchFilter

    def getSearchFilterData(self):
        """Returns persistent stored search filter data"""
        storage =  self.getFilterStorage()
        for k, v in storage.values():
            yield {'__name__': k, 'name': v.name}

    def getFilterStorage(self):
        """Returns the persistent filter storage"""
        return self.request.member.filters

    def addSearchFilter(self, name):
        """Add SearchFilter to mongodb"""
        # get filter from session
        searchFilter = self.searchFilter
        searchFilter.name = name
        storage = self.getFilterStorage()
        key = storage.add(searchFilter)
        # and load search filter
        self.loadSearchFilter(key)
        return key

    def loadSearchFilter(self, key):
        """Load SearchFilter from mongodb"""
        session = self.searchSession
        storage = self.getFilterStorage()
        searchFilter = storage.get(key)
        if searchFilter is not None:
            self._searchFilter = searchFilter
            self.saveFilter()
            self.resetResults()
            return searchFilter

    def removeSearchFilter(self, key):
        try:
            storage = self.getFilterStorage()
            del storage[key]
            self.searchSession.removeFilter(self.filterName)
            self._searchFilter = None
            self.resetResults()
            return True
        except KeyError, e:
            return False

    def saveFilter(self):
        """Save new or update existing filter"""
        self.searchSession.addFilter(self.filterName, self.searchFilter)

    def resetResults(self):
        """Knows how to reset the search result after loading a new filter"""
        pass

    def setupCriterionRows(self):
        """Setup criterion rows"""
        self.criterionRows = []
        if self.showFilter:
            if self.searchForm is not None:
                searchForm = self.searchForm
            else:
                searchForm = self
            append = self.criterionRows.append
            changed = False
            for criterion in self.searchFilter.criteria:
                row = zope.component.getMultiAdapter(
                    (criterion, self.request), name=self.rowName)
                row.__name__ = row.criterionName
                row.__parent__ = searchForm
                row.searchForm = searchForm
                row.searchPage = self
                row.update()
                if row.save():
                    changed = True
                append(row)
            self.criterionRows.sort(key=lambda form:form.context.weight)
            if changed:
                self.saveFilter()

    def doHandleAddCriterion(self, action):
        name = self.request.get(self.addCriterionName, None)
        if name is not None:
            self.searchFilter.createAndAddCriterion(name)
            self.setupCriterionRows()
            self.saveFilter()
            self.filterStatus = _('New criterion added')

    def doHandleRemoveCriterion(self, action):
        name = self.request.get(self.removeCriterionName, None)
        changed = False
        if name is not None:
            for row in self.criterionRows:
                if name == row.context.__name__:
                    changed = True
                    self.searchFilter.removeCriterion(row.context)
        if changed:
            self.setupCriterionRows()
            self.saveFilter()
            self.filterStatus = _('Criterion removed')

    def doHandleFilterSearch(self, action):
        # filter update happens on each request in setupCriterionRows
        pass

    def doHandleClearCriteria(self, action):
        self.searchSession.removeFilter(self.filterName)
        self._searchFilter = None
        self.resetResults()
        self.setupCriterionRows()
        self.saveFilter()
        self.filterStatus = _('Criteria cleared')

    def renderFilter(self):
        return self.filterTemplate()


# search form
class J01SearchForm(J01SearchFormMixin, jsform.JSONRPCForm):
    """J01 search form including filter management."""

    zope.interface.implements(interfaces.IJ01SearchForm)

    # default form vars
    prefix = 'form'
    ignoreContext = True
    contentTargetExpression = '#content'

    @property
    def addCriterionActionURL(self):
        return self.action

    @property
    def searchByFilterActionURL(self):
        return self.action

    @property
    def clearFilterActionURL(self):
        return self.action

    @property
    def criterionFormActionURL(self):
        return self.action

    @property
    def removeCriterionURL(self):
        return self.action

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['addCriterion'])
    def handleAddCriterion(self, data):
        return self.doHandleAddCriterion(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['removeCriterion'])
    def handleRemoveCriterion(self, data):
        self.doHandleRemoveCriterion(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['searchByFilter'])
    def handleSearch(self, data):
        return self.doHandleFilterSearch(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['clearFilter'])
    def handleClearCriteria(self, data):
        return self.doHandleClearCriteria(data)

    @property
    def searchActions(self):
        # support action lookup
        return self.actions

    def update(self):
        # first setup criterion rows
        self.setupCriterionRows()
        # second setup form and process actions
        super(J01SearchForm, self).update()


# search sub form used for search page
class J01SearchSubForm(jsform.JSONRPCForm):
    """J01SearchFrom button actions implemented as sub form
    
    The button action will dispatch the action calls to the __parent__ instance
    which must implement the J10SearchFomr API.

    """

    ignoreContext = True

    def __init__(self, context, request, parent):
        self.context = context
        self.request = request
        self.__parent__ = parent

    @property
    def action(self):
        # let the sub form act with the __parent__ page url
        return self.__parent__.pageURL

    @property
    def addCriterionActionURL(self):
        return self.action

    @property
    def searchByFilterActionURL(self):
        return self.action

    @property
    def clearFilterActionURL(self):
        return self.action

    @property
    def criterionFormActionURL(self):
        return self.action

    @property
    def removeCriterionURL(self):
        return self.action

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['addCriterion'])
    def handleAddCriterion(self, data):
        return self.__parent__.doHandleAddCriterion(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['removeCriterion'])
    def handleRemoveCriterion(self, data):
        self.__parent__.doHandleRemoveCriterion(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['searchByFilter'])
    def handleSearch(self, data):
        return self.__parent__.doHandleFilterSearch(data)

    @jsform.jsonRPCButtonHandler(IJ01SearcherButtons['clearFilter'])
    def handleClearCriteria(self, data):
        return self.__parent__.doHandleClearCriteria(data)

    def update(self):
        # first setup criterion rows from search form
        self.__parent__.setupCriterionRows()
        # second setup form and process actions
        super(J01SearchSubForm, self).update()


# search page mixin
class J01SearchPageMixin(J01SearchFormMixin):
    """JSON-RPC page mixin offering a J01SearchSubForm as searchForm attribute
    
    Note: only the button actions are supported by the sub form all other
    methods are implemented in this page.

    The __parent__ action will get executed before this update call which means
    all relevant parts must be done in the this instance, e.g. change batch
    size, sort order etc.

    """

    zope.interface.implements(interfaces.IJ01SearchPage)

    searchForm = None
    searchFormFactory = J01SearchSubForm
    searchFormName = 'search'
    searchFormPrefix = 'search'

    @property
    def searchActions(self):
        # support action lookup, this let us use the filter template
        return self.searchForm.actions

    def update(self):
        # first setup form and process actions
        self.searchForm = self.searchFormFactory(self.context, self.request,
            self)
        self.searchForm.__name__ = self.searchFormName
        self.searchForm.prefix = self.searchFormPrefix
        self.searchForm.update()
        # second update search result
        super(J01SearchPageMixin, self).update()


# search page
class J01SearchPage(J01SearchPageMixin, jspage.JSONRPCPage):
    """JSON-RPC page"""
