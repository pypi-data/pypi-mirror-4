import traceback
import sys
from StringIO import StringIO


def replace_error_handler():
    from invenio import errorlib

    def error_handler(stream='error',
                      req=None,
                      prefix='',
                      suffix='',
                      alert_admin=False,
                      subject=''):
        print traceback.format_exc()[:-1]

    errorlib.register_exception = error_handler


def wrap_warn():
    import warnings

    def wrapper(warn_fun):
        def fun(*args, **kwargs):
            traceback.print_stack()
            return warn_fun(*args, **kwargs)
        return fun

    warnings.warn = wrapper(warnings.warn)

from invenio.webinterface_handler_wsgi import SimulatedModPythonRequest, \
                                              SERVER_RETURN, \
                                              register_exception, \
                                              is_mp_legacy_publisher_path, \
                                              mp_legacy_publisher, \
                                              CFG_WSGI_SERVE_STATIC_FILES, \
                                              invenio_handler, \
                                              OK, \
                                              DONE, \
                                              alert_admin_for_server_status_p, \
                                              generate_error_page, \
                                              is_static_path




try:
    from invenio.webinterface_handler_flask import create_invenio_flask_app
except ImportError:
    from invenio.webinterface_handler_wsgi import application
else:
    application = create_invenio_flask_app()
