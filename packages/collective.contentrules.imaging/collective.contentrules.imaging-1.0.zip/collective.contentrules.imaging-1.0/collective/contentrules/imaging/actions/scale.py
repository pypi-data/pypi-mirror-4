from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm

from Products.CMFPlone import PloneMessageFactory as _
from plone.app.imaging.utils import getAllowedSizes
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory


class ScalesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        allowed_sizes = getAllowedSizes()
        items = [SimpleTerm(size, size, size) for size in allowed_sizes]
        return SimpleVocabulary(items)

ScalesVocabularyFactory = ScalesVocabulary()
SCALES_VOCAB = "collective.contentrules.imaging.vocabularies.Scales"


class IScaleAction(Interface):
    """
       Interface for the configurable aspects of a scale action.
    """

    scales = schema.List(title=_(u"Image scales"),
                           value_type=schema.Choice(title=_(u"Image scale"),
                                            vocabulary=SCALES_VOCAB)
                         )


class ScaleAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IScaleAction, IRuleElementData)

    scales = []
    element = 'collective.contentrules.imaging.actions.Scale'

    @property
    def summary(self):
        return _(u"Scale image")


class ScaleActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IScaleAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        image = self.event.object
        traverse = self.context.REQUEST.traverseName
        for scale in self.element.scales:
            traverse(image, 'image_%s' % scale)


class ScaleAddForm(AddForm):
    """An add form for scale actions.
    """
    form_fields = form.FormFields(IScaleAction)
    label = _(u"Add Scale Action")
    description = _(u"A scale action create scales of image")
    form_name = _(u"Configure element")

    def create(self, data):
        a = ScaleAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class ScaleEditForm(EditForm):
    """An edit form for move rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IScaleAction)
    label = _(u"Edit Scale Action")
    description = _(u"A scale action create scales of image")
    form_name = _(u"Configure element")
