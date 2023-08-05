from zope import component
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry
from collective.diggdigg.settings import Settings
from collective.diggdigg.buttons.button import IButton, cmp_button


class DiggDigg(ViewletBase):
    """DiggDigg base viewlet"""
    index = ViewPageTemplateFile("diggdigg.pt")

    def render(self):
        if self.available:
            self.update()
            return self.index()
        return u""

    @property
    def available(self):
        settings = self.registry.forInterface(Settings)
        if settings and settings.filter_types:
            return self.context.portal_type in settings.filter_types
        return True

    def update(self):
        ViewletBase.update(self)
        if not hasattr(self, 'registry'):
            self.registry = component.getUtility(IRegistry)

        buttons = list(component.getAdapters((self.context, self.request),
                                             IButton))
        settings = self.registry.forInterface(Settings)

        if settings and settings.buttons:
            self.buttons = [button for name, button in buttons\
                            if name in settings.buttons]
        else:
            self.buttons = [button for name, button in buttons]

        self.buttons.sort(cmp=cmp_button)

    def get_globalsettings(self):
        return "var dd_offset_from_content = 51;\
                var dd_top_offset_from_content = 51;"
