from collective.diggdigg.buttons import button

ATTRIBUTES = ("counter", "showzero", "url")

REGISTRY_KEY = "collective.diggdigg.linkedin."


class Linkedin(button.Button):
    """documentation:
    https://developer.linkedin.com/share-plugin
    """
    snippet = """<script src="http://platform.linkedin.com/in.js" type="text/javascript"></script>
    <div class="dd-linkedin-share"><div %s></div></div>
    <!--<script type="IN/Share" s></script>-->
    """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 500

    def update(self):
        super(Linkedin, self).update()
        self.showzero = "true"  # "false"
        self.counter = "top"  # "right"
        self.url = self.context.absolute_url()

    def index(self):
        attributes = self.get_data_attributes()
        return self.snippet % attributes
