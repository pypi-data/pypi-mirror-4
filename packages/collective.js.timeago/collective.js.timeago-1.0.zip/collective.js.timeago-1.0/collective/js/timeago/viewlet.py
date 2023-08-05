from plone.app.layout.viewlets.common import ViewletBase

SCRIPT_TAG = """<script type="text/javascript"
  src="%s/++resource++collective.js.timeago/locales/jquery.timeago.%s.js"></script>"""

class L10nTimeAgo(ViewletBase):
    """Load L10N for this javascript"""

    def update(self):
        super(L10nTimeAgo, self).update()
        self.lang = self.portal_state.language()

    def index(self):
        return SCRIPT_TAG % (self.site_url, self.lang)
