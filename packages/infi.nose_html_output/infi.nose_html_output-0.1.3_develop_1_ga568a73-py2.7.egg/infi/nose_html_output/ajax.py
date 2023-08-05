import threading
import webbrowser
try:
    from http.server import HTTPServer
    from http.server import BaseHTTPRequestHandler
    from urllib.request import pathname2url
    from queue import Queue
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urllib import pathname2url
    from Queue import Queue
import os
import shutil

# we send this via JSONP to the local file js to run
REFRESH_JS = "document.location.reload(true);"

def get_ajax_handler_class(queue, file_path):
    # only way to pass parameters to the handler class is by returning it from a function
    
    class AjaxHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            import json
            result = queue.get()
            while not queue.empty():
                result = queue.get()
            self.send_response(200)
            self.send_header("Content-type", "text/js")
            self.send_header("Content-length", len(result))
            self.end_headers()
            try:
                self.wfile.write(bytes(str(result), "ascii"))
            except TypeError:
                # python 2.7
                self.wfile.write(str(result))
            self.wfile.close()
                
        def log_message(self, format, *args):
            return
                
    return AjaxHandler

class AjaxServer(object):
    def __init__(self, use_ajax, do_open_browser, local_file, port):
        global file_path
        self._use_ajax = use_ajax
        self._do_open_browser = do_open_browser
        self._port = port
        self._local_file = os.path.abspath(local_file)
        self._queue = Queue()
        self._bind_address = 'localhost'
        self._url_to_localfile = 'file:' + pathname2url(self._local_file)
        self._url_to_webfile = 'http://%s:%s/%s' % (self._bind_address, self._port, os.path.basename(self._local_file))

    def _open_browser(self, url, timeout):
        def _open_browser():
            webbrowser.open(url)
        thread = threading.Timer(timeout, _open_browser)
        thread.daemon = True
        thread.start()

    def _start_server(self):
        server_address = (self._bind_address, self._port)
        self._server = HTTPServer(server_address, get_ajax_handler_class(self._queue, self._local_file))
        def _start_server():
            self._server.serve_forever()
        thread = threading.Thread(target=_start_server)
        thread.daemon = True
        thread.start()

    def trigget_start(self):
        if self._use_ajax:
            self._start_server()
        if self._do_open_browser:
            if self._use_ajax:
                self._open_browser(self._url_to_localfile, 1)
            else:
                self._open_browser(self._url_to_localfile, 0)

    def trigget_refresh(self):
        if self._use_ajax:
            self._queue.put(REFRESH_JS)

    def trigger_end(self):
        self.trigget_refresh()
        if self._use_ajax:
            self._server.shutdown()

def test():
    server = AjaxServer(True, True, "index.html", 16193)
    server.trigget_start()
    import time
    time.sleep(5)
    server.trigget_refresh()
    time.sleep(5)
    server.trigger_end()

if __name__ == "__main__":
    test()