from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib.interfaces import ConversionError
from zope.formlib.interfaces import  MissingInputError
from Products.CMFCore.utils import getToolByName


class ShoppinglistWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('widget.pt')

    def _getFormInput(self):
        value = super(ShoppinglistWidget, self)._getFormInput()
        # Make sure that we always retrieve a list object from the
        # request, even if only a single item or nothing has been
        # entered
        if value is None:
            value = []
        if not isinstance(value, list):
            value = [value]
        return value

    def getInputValue(self):
        self._error = None
        field = self.context

        # form input is required, otherwise raise an error
        if not self.hasInput():
            raise MissingInputError(self.name, self.label, None)

        # convert input to suitable value - may raise conversion error
        try:
            value = self._toFieldValue(self._getFormInput())
        except ConversionError, error:
            # ConversionError is already a WidgetInputError
            self._error = error
            raise self._error

        # allow missing values only for non-required fields
        if value == field.missing_value and not field.required:
            return value

        # Skip validation, is not needed in our case

        return value

    def _getFormValue(self):
        """Returns a value suitable for use in an HTML form.

        Detects the status of the widget and selects either the input value
        that came from the request, the value from the _data attribute or the
        default value.
        """
        mtool = getToolByName(self.context.context, 'portal_membership')
        pc = getToolByName(self.context.context, 'portal_catalog')
        member = mtool.getAuthenticatedMember()
        sl = member.getProperty('shoppinglist', tuple())
        brains = pc(UID=sl)

        input_value = list()
        for b in brains:
            if b is not None:
                input_value.append(dict(uid=b.UID, brain=b))

        return input_value

    def hasInput(self):
        return (self.name + '.marker') in self.request.form
