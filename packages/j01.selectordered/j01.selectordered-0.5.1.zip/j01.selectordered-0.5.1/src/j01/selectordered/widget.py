###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Password widget
$Id: widget.py 3469 2012-11-22 00:23:00Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.i18n
import zope.i18nmessageid
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.select
import z3c.form.browser.orderedselect
from z3c.template.template import getPageTemplate

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget

import j01.selectordered.layer
from j01.selectordered import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


ORDERED_SELECT_WIDGET_TEMPLATE = """
<script type="text/javascript">
jQuery(function(){
    $('#%(btnAdd)s').click(function(){
        $('#%(source)s option:selected').each( function() {
            var option = $(document.createElement('option'));
            option.val($(this).val());
            option.append($(this).text());
            $('#%(target)s').append(option);
            $(this).remove();
            // setup hidden fields
            $('input[name="%(selectedFieldName)s"]').remove();
            $('#%(target)s option').each( function() {
                $('<input/>').attr({
                    type: 'hidden',
                    name: '%(selectedFieldName)s',
                    value: $(this).val()}).appendTo('#%(selectedFieldContainer)s');
            });
        });
    });
    $('#%(btnRemove)s').click(function(){
        $('#%(target)s option:selected').each( function() {
            var option = $(document.createElement('option'));
            option.val($(this).val());
            option.append($(this).text());
            $('#%(source)s').append(option);
            $(this).remove();
            // setup hidden fields
            $('input[name="%(selectedFieldName)s"]').remove();
            $('#%(target)s option').each( function() {
                $('<input/>').attr({
                    type: 'hidden',
                    name: '%(selectedFieldName)s',
                    value: $(this).val()}).appendTo('#%(selectedFieldContainer)s');
            });
        });
    });
    $('#%(btnUp)s').bind('click', function() {
        $('#%(target)s option:selected').each( function() {
            var options = $('#%(target)s option');
            var newPos = options.index(this) - 1;
            if (newPos > -1) {
                var option = $(document.createElement('option'));
                option.val($(this).val());
                option.attr({'selected':''});
                option.append($(this).text());
                options.eq(newPos).before(option);
                $(this).remove();
            }
        });
        // re-order hidden fields
        $('input[name="%(selectedFieldName)s"]').remove();
        $('#%(target)s option').each( function() {
            $('<input/>').attr({
                type: 'hidden',
                name: '%(selectedFieldName)s',
                value: $(this).val()}).appendTo('#%(selectedFieldContainer)s');
        });
    });
    $('#%(btnDown)s').bind('click', function() {
        var options = $('#%(target)s option');
        var countOptions = options.size();
        $('#%(target)s option:selected').each( function() {
            var newPos = options.index(this) + 1;
            if (newPos < countOptions) {
                var option = $(document.createElement('option'));
                option.val($(this).val());
                option.attr({'selected':''});
                option.append($(this).text());
                options.eq(newPos).after(option);
                $(this).remove();
            }
        });
        // re-order hidden fields
        $('input[name="%(selectedFieldName)s"]').remove();
        $('#%(target)s option').each( function() {
            $('<input/>').attr({
                type: 'hidden',
                name: '%(selectedFieldName)s',
                value: $(this).val()}).appendTo('#%(selectedFieldContainer)s');
        });
    }); 
});
</script>
"""

def getOrderedSelectWidgetButton(id, css, content):
    if css:
        css = ' class="%s"' % css
    else:
        css = ''
    return '<a href="JavaScript:void(0);" id="%s"%s>%s</a>' % (
        id, css, content)


class OrderedSelectWidget(z3c.form.browser.orderedselect.OrderedSelectWidget):
    """Ordered-Select widget implementation with JQuery template."""

    zope.interface.implementsOnly(interfaces.IOrderedSelectWidget)

    klass = u'j01OrderedSelectWidget'
    css = u'j01-selectordered'

    selectFromTemplate = getPageTemplate('from')
    selectToTemplate = getPageTemplate('to')

    # btn labels
    @property
    def btnAddLabel(self):
        return zope.i18n.translate(_(u'add'), context=self.request)

    @property
    def btnRemoveLabel(self):
        return zope.i18n.translate(_(u'remove'), context=self.request)

    @property
    def btnUpLabel(self):
        return zope.i18n.translate(_(u'up'), context=self.request)

    @property
    def btnDownLabel(self):
        return zope.i18n.translate(_(u'down'), context=self.request)

    # ids
    @property
    def btnAddId(self):
        return '%s-btn-add' % self.id

    @property
    def btnRemoveId(self):
        return '%s-btn-remove' % self.id

    @property
    def btnUpId(self):
        return '%s-btn-up' % self.id

    @property
    def btnDownId(self):
        return '%s-btn-down' % self.id

    # css
    @property
    def btnAddCSS(self):
        return 'btnOrderedSelectAdd'

    @property
    def btnRemoveCSS(self):
        return 'btnOrderedSelectRemove'

    @property
    def btnUpCSS(self):
        return 'btnOrderedSelectUp'

    @property
    def btnDownCSS(self):
        return 'btnOrderedSelectDown'

    # btns
    @property
    def btnAdd(self):
        return getOrderedSelectWidgetButton(self.btnAddId, self.btnAddCSS,
            self.btnAddLabel)

    @property
    def btnRemove(self):
        return getOrderedSelectWidgetButton(self.btnRemoveId, self.btnRemoveCSS,
            self.btnRemoveLabel)

    @property
    def btnUp(self):
        return getOrderedSelectWidgetButton(self.btnUpId, self.btnUpCSS,
            self.btnUpLabel)

    @property
    def btnDown(self):
        return getOrderedSelectWidgetButton(self.btnDownId, self.btnDownCSS,
            self.btnDownLabel)

    # hidden input data
    @property
    def selectedFieldName(self):
        return '%s:list' % self.name

    # ordered selected item container (used for hidden ordered items)
    @property
    def selectedFieldContainer(self):
        return '%s-container' % self.id

    # javascript
    @property
    def javascript(self):
        source = '%s-from' % self.id
        target = '%s-to' % self.id
        return ORDERED_SELECT_WIDGET_TEMPLATE % (
            {'source': source, 'target': target,
             'selectedFieldName': self.selectedFieldName,
             'selectedFieldContainer': self.selectedFieldContainer,
             'btnAdd': self.btnAddId, 'btnRemove': self.btnRemoveId,
             'btnUp': self.btnUpId, 'btnDown': self.btnDownId})

    @property
    def selectFrom(self):
        """Render select from element tenmplate"""
        return self.selectFromTemplate()
    
    @property
    def selectTo(self):
        """Render select to element tenmplate"""
        return self.selectToTemplate()


# ordered select widget
@zope.component.adapter(zope.schema.interfaces.ISequence,
                        j01.selectordered.layer.IOrderedSelectLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def OrderedSelectFieldWidget(field, request):
    """IFieldWidget factory for OrderedSelectWidget."""
    return z3c.form.widget.FieldWidget(field, OrderedSelectWidget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for OrderedSelectWidget."""
    return OrderedSelectFieldWidget(field, request)


# get
def getOrderedSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, OrderedSelectWidget(request))


# setup
def setUpOrderedSelectWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(OrderedSelectWidget, **kw)
