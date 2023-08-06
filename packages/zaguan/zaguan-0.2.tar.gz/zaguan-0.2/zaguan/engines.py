try:
    import webkit
except ImportError:
    pass

try:
    import gtkmozembed
except ImportError:
    pass

class WebKitMethods(object):

    @staticmethod
    def create_browser():
        settings = webkit.WebSettings()
        #settings.set_property('enable-xss-auditor', False)
        # todas las settings en http://webkitgtk.org/reference/webkitgtk/stable/WebKitWebSettings.html
        settings.set_property('enable-default-context-menu', False)

        webview = webkit.WebView()
        webview.set_settings(settings)
        return webview

    @staticmethod
    def inject_javascript(browser, script):
        browser.execute_script(script)

    @staticmethod
    def connect_title_changed(browser, callback):
        def callback_wrapper(widget, frame, title): callback(title)
        browser.connect('title-changed', callback_wrapper)

    @staticmethod
    def open_uri(browser, uri):
        browser.open(uri)


class GtkMozEmbedMethods(object):

    @staticmethod
    def create_browser():
        return gtkmozembed.MozEmbed()

    @staticmethod
    def inject_javascript(browser, script):
        uri = 'javascript:%s' % urllib.quote(script + '\n;void(0);')
        browser.load_url(uri)

    @staticmethod
    def connect_title_changed(browser, callback):
        # XXX: probably you should cross your fingers and hope browser
        #      isn't sending title messages too quickly...?
        def callback_wrapper(*args): callback(browser.get_title())
        browser.connect('title', callback_wrapper)

    @staticmethod
    def open_uri(browser, uri):
        browser.load_url(uri)