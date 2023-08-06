# -*- coding: utf-8 -*-
import urllib

from json import dumps, loads

from zaguan.container import launch_browser


class WebContainerController(object):
    def __init__(self):
        self.processors = []

    """Clase base para los controladores de los contenedores web."""
    def on_navigation_requested(self, elem, view, frame, req, data=None):
        """Callback que se ejecuta cada vez que se carga una URI dentro del
        objeto webkit."""
        uri = req.get_uri()
        self.process_uri(uri)

    def process_uri(self, uri):
        """Procesa la URI y la separa en partes para llamar a process_action."""
        for processor in self.processors:
            processor(uri)

    def set_pantalla(self, pantalla, **kwargs):
        """Envia un comando de cambio de pantalla a la interfaz Web"""
        self.enviar_comando("cambiar_pantalla", [pantalla, kwargs])

    def enviar_comando(self, comando, data=None):
        """Genera el comando Javascript a enviar a la interfaz web y lo envia.
        """
        json_data = dumps(data).replace("\\\"", "\\\'")
        self.send_function("run_op('%s', '%s')" % (comando, json_data))

    def get_browser(self, uri, debug=False):
        """Obtiene el objeto browser y lo prepara para poder ser usada en este
        contexto.

        Devuelve el objeto browser y setea la funcion de envio para la clase.
        """
        browser, web_send = launch_browser(uri, echo=debug)
        self.send_function = web_send

        browser.connect("resource-request-starting",
                        self.on_navigation_requested)
        return browser

    def add_processor(self, url_word, callback):
        def _inner(uri):
            scheme, path = uri.split(':', 1)
            if scheme == "http":
                parts = path.split("/")[2:]
                if parts[0] == url_word:
                    remain = parts[1]
                elif parts[1]  == url_word:
                    remain = parts[2]
                else:
                    remain = None
                if remain is not None:
                    try:
                        action, data = remain.split("?")
                    except ValueError:
                        action = remain
                        data = "null"

                    data = loads(urllib.unquote(data))
                    return callback(action, data)

        self.processors.append(_inner)
