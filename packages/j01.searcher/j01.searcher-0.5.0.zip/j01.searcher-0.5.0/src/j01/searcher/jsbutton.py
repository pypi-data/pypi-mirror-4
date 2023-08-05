##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""

import zope.i18nmessageid
from zope.traversing.browser import absoluteURL

from j01.jsonrpc import jsbutton

_ = zope.i18nmessageid.MessageFactory('p01')


# IJSButtons
class CriterumFormButton(jsbutton.JSONRPCButton):
    """Criterion Form button which uses the criterionFormActionURL as url"""

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        return None

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        return """
                $('#%s').on('click', '#%s', function(){
                    proxy = getJSONRPCProxy('%s');
                    proxy.addMethod('j01FormProcessor', %s);
                    var data = {'formRemoveCriterion':'0', 'j01FormHandlerName':'removeCriterion'};
                    proxy.j01FormProcessor(data);
                    return false;
                });
            """ % (formId, action.id, action.form.criterionFormActionURL,
                   self.callback)
