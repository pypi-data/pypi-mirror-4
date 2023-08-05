from collective.diggdigg.buttons import button

ATTRIBUTES = ("url", )

REGISTRY_KEY = "collective.diggdigg.flattr."


class Flattr(button.Button):
    """documentation:
    http://developers.flattr.net/button/
    """
    snippet = """
<a class="FlattrButton" style="display:none;" href="%(url)s" lang="%(lang)s" title="%(title)s">flattr</a>
<script type="text/javascript">
/* <![CDATA[ */
(function() {
    var s = document.createElement('script');
    var t = document.getElementsByTagName('script')[0];

    s.type = 'text/javascript';
    s.async = true;
    s.src = '//api.flattr.com/js/0.6/load.js?mode=auto';

    t.parentNode.insertBefore(s, t);
 })();
/* ]]> */
</script>"""
    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 700

    def update(self):
        super(Flattr, self).update()
        self.count = "vertical"

    def index(self):
        info = {"url": self.context.absolute_url(),
                "title": self.context.Title(),
                "lang": self.portal_state.language()}
        return self.snippet % info
