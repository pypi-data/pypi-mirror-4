from collective.diggdigg.buttons.button import Button

ATTRIBUTES = ('size', 'annotation', 'locale')
REGISTRY_KEY = "collective.diggdigg.plusone."


class PlusOne(Button):
    """documentation:
    https://developers.google.com/+/plugins/+1button/
    """
    snippet = """<div class="g-plusone" %(data)s></div>

<script type="text/javascript">
  %(lang)s

  (function() {
    var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
    po.src = 'https://apis.google.com/js/plusone.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
  })();
</script>
    """

    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 300

    def update(self):
        super(PlusOne, self).update()
        self.size = "tall"
        self.lang = self.portal_state.language()
        #self.annotation = "bubble" is default

    def index(self):
        attributes = self.get_data_attributes()
        lang = ''
        if self.lang:
            lang = "window.___gcfg = {lang: '%s'};" % self.lang

        result = self.snippet % {'data': attributes, 'lang': lang}
        return result
