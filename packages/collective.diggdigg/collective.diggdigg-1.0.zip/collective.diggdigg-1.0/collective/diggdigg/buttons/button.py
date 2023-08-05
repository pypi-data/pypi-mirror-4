import logging
from zope import component
from zope import interface
from zope import schema
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from plone.registry.interfaces import IRegistry
from Products.Archetypes.interfaces.base import IBaseObject
from zope.publisher.interfaces import IRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


logger = logging.getLogger("collective.diggdigg")


class IButton(interface.Interface):
    """a digg digg button"""
    weight = schema.Int(title=u"Weight")
    id = schema.ASCIILine(title=u"ID")


class Button(object):
    """base button"""
    interface.implements(IButton)
    component.adapts(IBaseObject, IRequest)
    settings_keys = []
    registry_key = ""
    id = "button"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.update()
        self.initialize_attributes()
        return self.index()

    def update(self):
        self.portal_state = component.getMultiAdapter((self.context,
                                                       self.request),
                                                  name="plone_portal_state")
        self.portal_registry = component.getUtility(IRegistry)
        self.weight = self.portal_registry.get(self.registry_key + 'weight',
                                               100)

    def initialize_attributes(self):
        for key in self.settings_keys:
            value = getattr(self, key, None)
            rvalue = self.portal_registry.get(self.registry_key + key, '')
            if value is None or value != rvalue and rvalue:
                setattr(self, key, rvalue)

    def log(self, message):
        logger.info(message)

    def get_data_attributes(self):
        attributes = ""
        for attribute in self.settings_keys:
            value = getattr(self, attribute)
            if value:
                key = "data-" + attribute.replace('_', '-')
                attributes += key + '="' + value + '" '
        #remove trailing space
        if attributes:
            attributes = attributes[0:-1]
        return attributes

def cmp_button(b1, b2):
    if b1.weight < b2.weight:
        return -1
    elif b1.weight > b2.weight:
        return 1
    if b1.id < b2.id:
        return -1
    elif b1.id > b2.id:
        return 1
    return 0


class ButtonsVocabulary(object):
    """buttons vocab"""
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        request = getRequest()
        cbuttons = list(component.getAdapters((context, request), IButton))
        buttons = [button for name, button in cbuttons]
        terms = [SimpleTerm(name, name, unicode(name)) for name in buttons]

        return SimpleVocabulary(terms)


ButtonsVocabularyFactory = ButtonsVocabulary()
