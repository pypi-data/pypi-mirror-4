from collective.diggdigg.buttons import button

ATTRIBUTES = ("count", )

REGISTRY_KEY = "collective.diggdigg.pinterest."


class PInterest(button.Button):
    """documentation:
    http://pinterest.com/about/goodies/#button_for_websites"
    """
    snippet = """
    <a href="http://pinterest.com/pin/create/button/?url=%(url)s&media=%(media)s"
      class="pin-it-button" count-layout="%(count)s"><img border="0" src="//assets.pinterest.com/images/PinExt.png" title="Pin It" /></a>
    <script type="text/javascript" src="//assets.pinterest.com/js/pinit.js"></script>
    """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 600

    def update(self):
        super(PInterest, self).update()
        self.count = "vertical"

    def index(self):
        info = {"url": self.context.absolute_url(),
                "media": None,  # I don't know what to push here
                "count": self.count}
        return self.snippet % info
