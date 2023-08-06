from zaguan.engines import WebKitMethods, GtkMozEmbedMethods
from zaguan.constants import WEBKIT, GECKO
from zaguan.functions import asynchronous_gtk_message, get_implementation

implementation_name = get_implementation()


def launch_browser(uri, echo=False):
    if implementation_name == WEBKIT:
        implementation = WebKitMethods
    elif implementation_name == GECKO:
        implementation = GtkMozEmbedMethods
    else:
        raise NotImplementedError("No hay motor web disponible")

    browser = implementation.create_browser()

    implementation.open_uri(browser, uri)

    def web_send(msg):
        if echo: print '<<<', msg
        asynchronous_gtk_message(implementation.inject_javascript)(browser, msg)

    return browser, web_send
