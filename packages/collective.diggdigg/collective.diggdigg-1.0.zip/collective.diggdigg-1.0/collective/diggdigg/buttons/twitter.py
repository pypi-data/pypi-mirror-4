from collective.diggdigg.buttons import button

ATTRIBUTES = ("text", "count", "via", "related", "hashtags", "size", "dnt",
              "lang")

REGISTRY_KEY = "collective.diggdigg.twitter."


class Twitter(button.Button):
    """documentation:
    https://dev.twitter.com/docs/tweet-button
    """
    snippet = """<a  href="https://twitter.com/share"
              class="twitter-share-button" %s>Tweeter</a>
        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
        """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 100

    def update(self):
        super(Twitter, self).update()
        registry = self.portal_registry
        self.text = self.context.Title()  # use title of the page
        self.lang = self.portal_state.language()  # fr
        # "", "horizontal", "vertical"
        self.count = registry.get(REGISTRY_KEY + 'count', "vertical")

    def index(self):
        attributes = self.get_data_attributes()
        return self.snippet % attributes
