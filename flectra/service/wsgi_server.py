import warnings
import flectra.http


def application(environ, start_response):

    warnings.warn("The WSGI application entrypoint moved from "
                  "flectra.service.wsgi_server.application to flectra.http.root "
                  "in 15.3.",
                  DeprecationWarning, stacklevel=1)
    return flectra.http.root(environ, start_response)
