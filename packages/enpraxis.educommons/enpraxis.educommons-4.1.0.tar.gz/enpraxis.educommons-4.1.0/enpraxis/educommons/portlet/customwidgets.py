from zope.app.form.browser import DropdownWidget, RadioWidget
from zope.app.form.browser.widget import renderElement
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from enpraxis.educommons import eduCommonsMessageFactory as _
from Products.CMFCore.utils import getToolByName


class EitherOrWidget(DropdownWidget):
    """ A widget that allows you to choose from a drop down, or type in an entry. """

    _messageNoValue = _(u'(Choose one)')
    seltext = _(u'Select from below:')
    nftext = _(u'If not found, type in the name below to create a new one:')

    def __init__(self, field, request):
        super(EitherOrWidget, self).__init__(field, field.vocabulary, request)

    def __call__(self):
        value = ''
        contents = []
        context = self.context.context

        # Render the Drop Down
	ts = getToolByName(context, 'translation_service')
        contents.append(self._div('formHelp', 
                                  ts.translate(self.seltext, context=context))) 
        contents.append(self._div('value', self.renderValue(value) ) )

        # Render the edit box
        contents.append(self._div('formHelp', 
                                  ts.translate(self.nftext, context=context)))
        contents.append(self._div('value', renderElement('input',
                                                         type='text',
                                                         name='.new'.join(self.name.split('.')),
                                                         id='%s.textfield' % self.name)))
                                                      
        contents.append(self._emptyMarker())

        return self._div(self.cssClass, "\n".join(contents))


class EitherOrNoValidateWidget(EitherOrWidget):
    """ A widget that implements EitherOr, but skips validation to allow dynamic options. """

    def getInputValue(self):
        return self._getFormInput()
        

class MultiPreSelectCheckBoxVocabularyWidget(MultiCheckBoxVocabularyWidget):
    """ A Multi check box widget that pre selects options. """

    def __init__(self, field, request):
        super(MultiPreSelectCheckBoxVocabularyWidget, self).__init__(field, request)
        self.templates = field.value_type.vocabulary.by_value.keys()

    def _getFormValue(self):
        return self.templates


def ChoiceRadioWidget(field, request):
    """ A radio widget with a None option """
    widget = RadioWidget(field, field.vocabulary, request)
    widget._messageNoValue = _("None")

    return widget

