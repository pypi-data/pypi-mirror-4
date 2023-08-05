from collective.diggdigg.buttons.button import Button

ATTRIBUTES = ('href', 'send', 'layout', 'show_faces', 'width', 'action',
              'locale')
REGISTRY_KEY = "collective.diggdigg.facebook."


class FacebookLike(Button):
    """documentation:
    https://developers.facebook.com/docs/reference/plugins/like/
    """
    snippet = """<div id="fb-root"></div>
    <script>(function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
    </script>
    <div class="fb-like" %s></div>"""

    settings_keys = ATTRIBUTES
    registry_key = REGISTRY_KEY
    weight = 200

    def update(self):
        super(FacebookLike, self).update()
        self.layout = 'box_count'
        self.locale = 'en_US'
        self.show_face = "false"

    def index(self):
        attributes = self.get_data_attributes()
        result = self.snippet % attributes
        return result
