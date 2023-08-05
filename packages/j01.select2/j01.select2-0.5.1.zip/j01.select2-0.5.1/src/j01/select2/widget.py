##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: widget.py 3127 2012-09-27 01:58:19Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.i18n
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL

import z3c.form.widget
import z3c.form.browser.widget
import z3c.form.browser.select
import z3c.form.browser.text
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget

from j01.select2 import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


j01_select2_template = """
<script type="text/javascript">
  $("#%s").select2({%s
  });
</script>
"""

NULL = object()


def j01Select2JavaScript(widgetExpression, data):
    """Select2 javaScript generator"""
    lines = []
    append = lines.append
    for key, value in data.items():
        # apply functions
        if value is None:
            continue
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is NULL:
            append("\n    %s: null" % key)
        elif key in ['id', 'matcher',
                     'formatSelection', 'formatResult', 'formatResultCssClass',
                     'formatNoMatches', 'formatLoadMore', 'formatSearching', 
                     'formatInputTooShort', 'formatSelectionTooBig',
                     'createSearchChoice',
                     'initSelection', 'tokenizer', 'tokenSeparators',
                     'query', 'ajax', 'data', 'tags', 'containerCss',
                     'containerCssClass', 'dropdownCss', 'dropdownCssClass']:
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, (list, int)):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    code = ','.join(lines)

    return j01_select2_template % (widgetExpression, code)


# select
class Select2WidgetBase(object):
    """Selects input widget"""

    # you can override this in your custom widget factory
    klass = u'j01Select2Widget'
    css = u'j01-select2'

    multiple = 'multiple'

    j01Select2MethodName = 'j01Select2Result'

    # select2 properties (see http://ivaynberg.github.com/select2/)
    # IGNORE means default value
    width = None
    minimumInputLength = 0
    minimumResultsForSearch = 10
    maximumSelectionSize = 0
    placeholder = None
    separator = '***' 
    allowClear = None
    closeOnSelect = True
    openOnEnter = True
    j01ID = None # prevent conflict with self.id
    matcher = None
    formatSelection = None
    formatResult = None
    formatResultCssClass = None
    createSearchChoice = None
    initSelection = None
    tokenizer = None
    tokenSeparators = [",", " "]
    query = None
    ajax = None
    data = None
    tags = None
    containerCss = None
    containerCssClass = None
    dropdownCss = None
    dropdownCssClass = None

    # i18n properties
    @property
    def formatNoMatches(self):
        msg = zope.i18n.translate(_("No matches found"), context=self.request)
        return 'function() {return "%s";}' % msg

    @property
    def formatInputTooShort(self):
        msg = zope.i18n.translate(
            _('Please enter "+(min - input.length)+" more characters'),
            context=self.request)
        return 'function(input, min) {return "%s";}' % msg

    @property
    def formatSelectionTooBig(self):
        msg = zope.i18n.translate(_('You can only select "+limit+" items'),
            context=self.request)
        return 'function(limit) {return "%s";}' % msg

    @property
    def formatLoadMore(self):
        msg = zope.i18n.translate(_('Loading more results...'),
            context=self.request)
        return 'function(pageNumber) {return "%s";}' % msg

    @property
    def formatSearching(self):
        msg = zope.i18n.translate(_("Searching..."),
            context=self.request)
        return 'function() {return "%s";}' % msg

    @property
    def j01Select2URL(self):
        return absoluteURL(self.form, self.request)

    def getSelect2Result(self, searchString, page):
        """Returns the select2 JSON-RPC call result as JSON data.

        Note: this is only a sample implementation which only returns the
        given searchString as selectable token. Add whatever you need to
        the existing result in your own implementation.

        {
             more: false,
             results: [
                { id: "mytag", text: "mytag" },
                { id: "another", text: "another" }
             ]
        }

        NOTE: if you set more = True, the search result will load new data on
        scrolling to the end. This means you to return more=False or there must
        new data where we can fetch.

        NOTE: return the searchString too if you like to offer text input,
        otherwise the given searchString is not selectable as input in the
        result.

        """
        searchString = searchString.strip()
        more = False
        # return ourself or we will miss that term in our result
        results = [{'id': searchString+'1', 'text': searchString}]
        return {'more': more, 'results': results}

    @property
    def settings(self):
        return {'width': self.width,
                'minimumInputLength': self.minimumInputLength,
                'minimumResultsForSearch': self.minimumResultsForSearch,
                'maximumSelectionSize': self.maximumSelectionSize,
                'placeholder': self.placeholder,
                'separator': self.separator,
                'allowClear': self.allowClear,
                'closeOnSelect': self.closeOnSelect,
                'openOnEnter': self.openOnEnter,
                'id': self.j01ID,
                'matcher': self.matcher,
                'formatSelection': self.formatSelection,
                'formatResult': self.formatResult,
                'formatResultCssClass': self.formatResultCssClass,
                'formatNoMatches': self.formatNoMatches,
                'formatLoadMore': self.formatLoadMore,
                'formatSearching': self.formatSearching,
                'formatInputTooShort': self.formatInputTooShort,
                'formatSelectionTooBig': self.formatSelectionTooBig,
                'createSearchChoice': self.createSearchChoice,
                'initSelection': self.initSelection,
                'tokenizer': self.tokenizer,
                'tokenSeparators': self.tokenSeparators,
                'query': self.query,
                'ajax': self.ajax,
                'data': self.data,
                'tags': self.tags,
                'containerCss': self.containerCss,
                'containerCssClass': self.containerCssClass,
                'dropdownCss': self.dropdownCss,
                'dropdownCssClass': self.dropdownCssClass,
               }

    @property
    def javaScript(self):
        return j01Select2JavaScript(self.id, self.settings)


class Select2Widget(Select2WidgetBase, z3c.form.browser.select.SelectWidget):
    """Selects input widget"""

    zope.interface.implementsOnly(interfaces.ISelect2Widget)


# tag list
TAG_INIT_SELECTION_SCRIPT = """function(element, callback) {
        var data = [];
        $(element.val().split("%s")).each(function () {
            data.push({id: this, text: this});
        });
        callback(data);
    }"""

# generic JSON-RPC method for result lookup supporting initial result data
# adding search string as token and JSON-RPC call if query bigger then
# minimumInputLength
RESULT_QUERY_SCRIPT = """function(query) {
    if (query.term.length > %(minimumInputLength)s) {
        var fieldName = '%(fieldName)s';
        proxy = getJSONRPCProxy('%(j01Select2URL)s');
        proxy.addMethod('%(j01Select2MethodName)s', query.callback, 'j01Select2');
        proxy.%(j01Select2MethodName)s(fieldName, query.term, query.page);
    }else{
        var data = {results: []};
        if (query.term != '') {
            data.results.push({id: query.term, text: query.term});
        }
        var results = %(initData)s;
        if (results) {
            $(results).each(function () {
                data.results.push({id: this.id, text: this.text});
            });
        }
        query.callback(data);
    }
}"""


class TagListSelect2Widget(Select2WidgetBase,
    z3c.form.browser.text.TextWidget):
    """Widget for IList of ITextLine
    
    This widget is based on a IList of ITextLine field, this means we can enter
    custom text data and the JSON-RPC callback is used for autosuggest
    useable input.

    """

    zope.interface.implementsOnly(interfaces.ITagListSelect2Widget)

    tags = []
    minimumInputLength = 2

    @property
    def initSelection(self):
        # catch value from input field
        return TAG_INIT_SELECTION_SCRIPT % self.separator

    @property
    def initData(self):
        # can provide initial value, "null" means no value
        return "null"

    @property
    def query(self):
        return RESULT_QUERY_SCRIPT % {
            'minimumInputLength': self.minimumInputLength,
            'fieldName': self.__name__,
            'j01Select2URL': self.j01Select2URL,
            'j01Select2MethodName': self.j01Select2MethodName,
            'initData': self.initData}


# single tag
SINGLE_TAG_INIT_SELECTION_SCRIPT = """function(element, callback) {
        var data = [];
        var value = element.val();
        if (value) {
            data.push({id: value, text: value});
        }
        callback(data);
    }"""

class SingleTagSelect2Widget(Select2WidgetBase,
    z3c.form.browser.text.TextWidget):
    """Widget for ITextLine
    
    This widget is based on a ITextLine field, this means we can enter
    custom text data and the JSON-RPC callback is used for autosuggest
    useable input.
    
    NOTE; this widget can only set one tag and not a list of tags.
    
    You can offer initial data and JSON-RPC autosuggest values.

    """

    zope.interface.implementsOnly(interfaces.ISingleTagSelect2Widget)

    tags = []
    minimumInputLength = 0
    # never maximumSelectionSize change for single item!
    maximumSelectionSize = 1

    @property
    def initSelection(self):
        # catch value from input field
        return SINGLE_TAG_INIT_SELECTION_SCRIPT

    @property
    def initData(self):
        # can provide initial value, "null" means no value
        return "null"

    @property
    def query(self):
        return RESULT_QUERY_SCRIPT % {
            'minimumInputLength': self.minimumInputLength,
            'fieldName': self.__name__,
            'j01Select2URL': self.j01Select2URL,
            'j01Select2MethodName': self.j01Select2MethodName,
            'initData': self.initData}


# livelist
LIVELIST_INIT_SELECTION_SCRIPT = """function(element, callback) {
    var data = [];
    var results = %s;
    element.val('');
    if (results !== null){
        $(results).each(function () {
            data.push({id: this.id, text: this.text});
        });
    }
    callback(data);
}"""

LIVELIST_RESULT_QUERY_SCRIPT = """function(query) {
    if (query.term.length > %(minimumInputLength)s) {
        var fieldName = '%(fieldName)s';
        proxy = getJSONRPCProxy('%(j01Select2URL)s');
        proxy.addMethod('%(j01Select2MethodName)s', query.callback, 'j01Select2');
        proxy.%(j01Select2MethodName)s(fieldName, query.term, query.page);
    }
}"""


class LiveListSelect2Widget(Select2WidgetBase,
    z3c.form.browser.widget.HTMLTextInputWidget,
    z3c.form.widget.SequenceWidget):
    """Widget for IList of IChoice"""

    zope.interface.implementsOnly(interfaces.ILiveListSelect2Widget)

    tags = []
    minimumInputLength = 2

    size = 25

    @property
    def dummyValue(self):
        # forces to invoke initSelection, an empty value prevents
        return self.noValueToken

    def extract(self, default=NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            if isinstance(value, basestring):
                # extract widget value and split by separator. If the value
                # is not a base string, it was set during form setup
                value = value.split(self.separator)
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value

    @property
    def j01Select2URL(self):
        return absoluteURL(self.form, self.request)

    @property
    def initSelection(self):
        """Set initial selected tags"""
        # catch value from input field
        res = "null"
        if self.value:
            if self.terms is None:
                self.updateTerms()
            # append existing values
            data = []
            for token in self.value:
                term = self.terms.getTermByToken(token)
                title = term.getTitle(self.request)
                data.append('{id: "%s", text: "%s"}' % (token, title))
            if len(data) > 0:
                res = "["
                res += ",".join(data)
                res += "]"
        return LIVELIST_INIT_SELECTION_SCRIPT % res

    @property
    def query(self):
        """Apply JSON-RPC based search concept"""
        return LIVELIST_RESULT_QUERY_SCRIPT % {
            'minimumInputLength': self.minimumInputLength,
            'fieldName': self.__name__,
            'j01Select2URL': self.j01Select2URL,
            'j01Select2MethodName': self.j01Select2MethodName}

    def getSelect2Result(self, searchString, page):
        """Search for new tags based on search string"""
        terms = self.terms.terms.search(searchString, page, self.size)
        page = terms.page
        pages = terms.pages
        more = terms.more
        groupName = None
        children = []
        results = []
        append = results.append
        for term in terms:
            if term.groupName is None:
                # add term data without using groups
                append({'id': term.token,
                        'text': term.title})
            elif groupName is None:
                # start with initial group
                groupName = term.groupName
                children = []
                children.append({'id': term.token,
                                 'text': term.title})
            elif term.groupName != groupName:
                # add children with previous groupName to result
                append({'text': groupName,
                        'children': children})
                # start with next group
                groupName = term.groupName
                children = []
                children.append({'id': term.token,
                                 'text': term.title})

        return {'more': more, 'results': results}


# HTML select element
@zope.interface.implementer(IFieldWidget)
def getSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    return z3c.form.widget.FieldWidget(field, Select2Widget(request))

@zope.interface.implementer(IFieldWidget)
def getSingleSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    widget = z3c.form.widget.FieldWidget(field, Select2Widget(request))
    widget.multiple = None
    return widget


# tagging
@zope.interface.implementer(IFieldWidget)
def getTagListSelect2Widget(field, request):
    """IFieldWidget factory for TagListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, TagListSelect2Widget(request))


# live list
@zope.interface.implementer(IFieldWidget)
def getLiveListSelect2Widget(field, request):
    """IFieldWidget factory for LiveListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, LiveListSelect2Widget(request))

