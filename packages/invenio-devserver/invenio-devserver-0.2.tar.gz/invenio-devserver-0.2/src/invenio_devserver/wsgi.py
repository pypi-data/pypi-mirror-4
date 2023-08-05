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


class BufferedWSGIRequest(SimulatedModPythonRequest):
    _response_buffer = None

    def start_response_wrapper(self, status, headers):
        self._response_status = status
        self._response_headers = headers
        self._response_buffer = StringIO()

        def write(bytes):
            self._response_buffer.write(bytes)
        return write

    def __init__(self, environ, start_response):
        self.__start_response_orig = start_response
        super(BufferedWSGIRequest, self).__init__(environ,
                                                  self.start_response_wrapper)

    def final_flush(self):
        if self._response_buffer:
            writer = self.__start_response_orig(self._response_status,
                                                  self._response_headers)
            writer(self._response_buffer.getvalue())


class WSGIRequest(SimulatedModPythonRequest):
    def final_flush(self):
        pass


def application(options, environ, start_response):
    """
    Entry point for wsgi.
    """
    if options.buffer_output:
        request = BufferedWSGIRequest
    else:
        request = WSGIRequest
    req = request(environ, start_response)

    try:
        try:
            possible_module, possible_handler = \
                            is_mp_legacy_publisher_path(environ['PATH_INFO'])
            if possible_module is not None:
                mp_legacy_publisher(req, possible_module, possible_handler)
            elif CFG_WSGI_SERVE_STATIC_FILES:
                possible_static_path = is_static_path(environ['PATH_INFO'])
                if possible_static_path is not None:
                    from invenio.bibdocfile import stream_file
                    stream_file(req, possible_static_path)
                else:
                    invenio_handler(req)
            else:
                invenio_handler(req)
            req.flush()
            req.final_flush()
        except SERVER_RETURN, status:
            status = int(str(status))
            if status not in (OK, DONE):
                req.status = status
                req.headers_out['content-type'] = 'text/html'
                admin_to_be_alerted = alert_admin_for_server_status_p(status,
                                                req.headers_in.get('referer'))
                if admin_to_be_alerted:
                    register_exception(req=req, alert_admin=True)
                if not req.response_sent_p:
                    start_response(req.get_wsgi_status(),
                                   req.get_low_level_headers(),
                                   sys.exc_info())
                return generate_error_page(req, admin_to_be_alerted)
            else:
                req.flush()
    finally:
        for (callback, data) in req.get_cleanups():
            callback(data)
    return []
