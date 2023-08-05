from collective.diggdigg.buttons import button

ATTRIBUTES = ("url", )

REGISTRY_KEY = "collective.diggdigg.viadeo."


class Viadeo(button.Button):
    """documentation:
    http://socialtoolbox.viadeo.com/?language=fr#recommend
    """
    snippet = """
<script type="text/javascript">var viadeoWidgetsJsUrl = document.location.protocol+"//widgets.viadeo.com";(function(){var e = document.createElement('script'); e.type='text/javascript'; e.async = true;e.src = viadeoWidgetsJsUrl+'/js/viadeowidgets.js'; var s = document.getElementsByTagName('head')[0]; s.appendChild(e);})();</script><div class="viadeo_widget_recommend"></div>
    """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 800

    def update(self):
        super(Viadeo, self).update()
        self.count = "top"

    def index(self):
        info = {"url": self.context.absolute_url(),
                "title": self.context.Title(),
                "lang": self.portal_state.language()}
        return self.snippet  # FIXME: the share button generators doesn't work
