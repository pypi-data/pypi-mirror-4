from collective.diggdigg.buttons import button

ATTRIBUTES = ("count")

REGISTRY_KEY = "collective.diggdigg.buffer."


class Buffer(button.Button):
    """documentation:
    http://bufferapp.com/extras/button
    """
    snippet = """<a href="http://bufferapp.com/add" class="buffer-add-button" %s>Buffer</a>
        <script type="text/javascript" src="http://static.bufferapp.com/js/button.js"></script>
    """
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 400

    def update(self):
        super(Buffer, self).update()
        self.count = "vertical"

    def index(self):
        attributes = self.get_data_attributes()
        return self.snippet % attributes
