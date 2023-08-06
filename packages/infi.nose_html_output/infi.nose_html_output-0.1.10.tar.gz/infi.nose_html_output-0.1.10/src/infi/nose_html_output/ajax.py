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
REFRESH_JS = """do_refresh('{}');
document_load();"""
RELOAD_JS = """run_spinner();
do_ajax_reload();"""

class AjaxHandler(BaseHTTPRequestHandler):
    queue = None
    
    def process_request(self, request, client_address):
        import socket
        try:
            return super(AjaxHandler, self).process_request(request, client_address)
        except socket.error:
            pass
        
    def do_GET(self):
        import json
        queue_param = self.queue.get()
        while not queue.empty():
            queue_param = self.queue.get()
        html_str, end = queue_param
        result = REFRESH_JS.format(html_str.replace("'", r"\'").replace('\n', '\\n'));
        if not end:
            result += RELOAD_JS
        self.send_response(200)
        self.send_header("Content-type", "text/javascript")
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
            
class AjaxServer(object):
    def __init__(self, use_ajax, do_open_browser, local_file, port):
        self._use_ajax = use_ajax
        self._do_open_browser = do_open_browser
        self._port = port
        self._local_file = os.path.abspath(local_file)
        self._queue = Queue()
        self._last_html_str = ""#open(local_file, "rb").read()
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
        AjaxHandler.queue = self._queue
        self._server = HTTPServer(server_address, AjaxHandler)
        def _start_server():
            self._server.serve_forever()
        thread = threading.Thread(target=_start_server)
        thread.daemon = True
        thread.start()

    def trigger_start(self):
        if self._use_ajax:
            self._start_server()
        if self._do_open_browser:
            if self._use_ajax:
                self._open_browser(self._url_to_localfile, 1)
            else:
                self._open_browser(self._url_to_localfile, 0)

    def trigger_refresh(self, html_str=None, end=False):
        if html_str is not None:
            self._last_html_str = html_str
        if self._use_ajax:
            self._queue.put((self._last_html_str, end))

    def trigger_end(self):
        self.trigger_refresh(end=True)
        if self._use_ajax:
            self._server.shutdown()

def test():
    server = AjaxServer(True, True, "index.html", 16193)
    server.trigger_start()
    import time
    time.sleep(5)
    server.trigger_refresh()
    time.sleep(5)
    server.trigger_end()

if __name__ == "__main__":
    test()