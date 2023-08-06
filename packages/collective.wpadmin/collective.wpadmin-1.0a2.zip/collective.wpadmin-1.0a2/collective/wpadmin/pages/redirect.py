from Products.Five.browser import BrowserView


class RedirectDashboard(BrowserView):
    """Redirect to wp-admin-dashboard"""
    def __call__(self):
        url = self.context.absolute_url() + '/wp-admin-dashboard'
        self.request.response.redirect(url)
