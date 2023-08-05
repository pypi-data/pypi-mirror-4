from collective.diggdigg.buttons import button

ATTRIBUTES = ("url", )

REGISTRY_KEY = "collective.diggdigg.reddit."


class Reddit(button.Button):
    """documentation:
    http://www.reddit.com/buttons
    """
    snippet = """
<script type="text/javascript">
  reddit_url = "%(url)s";
  reddit_title = "%(title)s";
</script>
<script type="text/javascript" src="http://www.reddit.com/static/button/button2.js"></script>
    """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 800

    def update(self):
        super(Reddit, self).update()

    def index(self):
        info = {"url": self.context.absolute_url(),
                "title": self.context.Title()}
        return self.snippet % info
