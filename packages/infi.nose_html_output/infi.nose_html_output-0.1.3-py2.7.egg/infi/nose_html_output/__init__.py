__import__("pkg_resources").declare_namespace(__name__)

import nose
from nose.plugins import Plugin
import nose.suite
import nose.case
from nose.util import isclass
from nose.plugins.logcapture import MyMemoryHandler

import os
import traceback
import logging
import lxml.etree as etree
import sys
import time

from pkg_resources import resource_filename
import shutil

from ajax import AjaxServer

# copied from unittest/result.py
def _is_relevant_tb_level(tb):
    return '__unittest' in tb.tb_frame.f_globals
def _count_relevant_tb_levels(tb):
    length = 0
    while tb and not _is_relevant_tb_level(tb):
        length += 1
        tb = tb.tb_next
    return length
def _exc_info_to_string(err, test):
    """Converts a sys.exc_info()-style tuple of values into a string."""
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and _is_relevant_tb_level(tb):
        tb = tb.tb_next

    if exctype is test.failureException:
        # Skip assert*() traceback levels
        length = _count_relevant_tb_levels(tb)
        msgLines = traceback.format_exception(exctype, value, tb, length)
    else:
        msgLines = traceback.format_exception(exctype, value, tb)
    return ''.join(msgLines)

class AutoStream(object):
    def __init__(self, filename):
        self._filename = filename
        self._file = None
        self._callback = []
    
    def write(self, buf):
        if self._file is None:
            self._file = open(self._filename, "w")
            for callback in self._callback:
                callback()
        self._file.write(buf)
        
    def add_callback(self, callback):
        self._callback.append(callback)
        
    def flush(self):
        if self._file is not None:
            self._file.flush()

class MultiStream(object):
    def __init__(self, streams):
        self.streams = streams
        
    def write(self, buf):
        for stream in self.streams:
            stream.write(buf)

class NosePlugin(Plugin):
    name = 'html-output'

    def options(self, parser, env=os.environ):
        parser.add_option("--open-browser", action="store_true", default=False,
                         help="If speicified, the default browser will be opened with the result page")
        parser.add_option("--use-ajax", action="store_true", default=False,
                         help="If speicified, the output page will automatically reload during the test run when" +
                                            "tests are updated. Note that this opens a local webserver and requires" +
                                            "port 16193 to be open and available.")
        super(NosePlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(NosePlugin, self).configure(options, conf)
        self._open_browser = options.open_browser
        self._use_ajax = options.use_ajax
        if not self.enabled:
            return
        
    def begin(self):
        self.total_tests = 0
        self.total_suites = 0
        self.total_modules = 0
        self.skipped_modules = 0
        self.skipped_suites = 0
        self.skipped_tests = 0
        self.failed_tests = 0
        
        self.res = []           # result (string) of latest module\suite\test
        self.trace = []         # traceback of latest module\suite\test
        self.log_name = []
        self.log_stream = []
        self.name = []          # name of latest module\suite\test
        self.stdouts = []
        self.setLogger()
        
        self.status = "running"
        
        self.root_dir_name = time.strftime("%Y_%m_%d__%H_%M_%S")
        os.mkdir(self.root_dir_name)
        shutil.copytree(resource_filename(__name__, "static"), os.path.join(self.root_dir_name, "static"))
        
        self.result_html_path = os.path.abspath(os.path.join(os.path.curdir, self.root_dir_name, "result.html"))
        self._ajax_server = AjaxServer(self._use_ajax, self._open_browser, self.result_html_path, 16193)
        self.create_html()
        self._ajax_server.trigget_start()
    
    def add_html_script(self, script):
        script = etree.SubElement(self.html_head, "script", {"src": script})
        script.text = ' '
        return script
    def create_html_head(self):
        self.html_head = etree.SubElement(self.html_root, "head")
        self.add_html_script("static/jquery-1.8.0.min.js")
        self.add_html_script("static/index.js")
        if self._use_ajax:
            self._ajax_scripts = []
            self._ajax_scripts.append(self.add_html_script("static/ajax_reload.js"))
            self._ajax_scripts.append(self.add_html_script("static/spin.min.js"))
            self._ajax_scripts.append(self.add_html_script("static/spinner.factory.js"))
        script = etree.SubElement(self.html_head, "link", {"rel": "stylesheet", "type": "text/css", "href": "static/index.css"})
        script.text = " "
    
    def create_html(self):
        self.html_root = etree.Element("html")
        self.create_html_head()
        self.html_body = etree.SubElement(self.html_root, "body")
        self.html_h1_parent = etree.SubElement(self.html_body, "div", {"class": "h1"})
        if self._use_ajax:
            self.html_spinner_element = etree.SubElement(self.html_h1_parent, "span", {"id": "running-spinner"})
            self.html_spinner_element.text = ' '
        self.html_h1 = etree.SubElement(self.html_h1_parent, "span")
        self.html_h2_1 = etree.SubElement(self.html_body, "div")
        self.html_h2_2 = etree.SubElement(self.html_body, "div")
        self.html_legend = etree.SubElement(self.html_body, "div", {"class": "legend"})
        self.html_legend.text = "C = Code | D = Description | L = Log"
        br = etree.SubElement(self.html_body, "br")
        self.html_body_main = etree.SubElement(self.html_body, "div", {"id": "main"})
        etree.SubElement(self.html_body, "br")
        self.update_html()
    
    def get_subtitle_label_for_html(self):
        sub_labels = []
        if self.skipped_modules > 0:
            sub_labels.append("%d modules skipped" % self.skipped_modules)
        if self.skipped_suites > 0:
            sub_labels.append("%d suites skipped" % self.skipped_suites)
        if self.skipped_tests > 0:
            sub_labels.append("%d tests skipped" % self.skipped_tests)
        if self.failed_tests > 0:
            sub_labels.append("%d tests failed" % self.failed_tests)
        return ", ".join(sub_labels)
        
    def update_html(self):
        status = {"running": "Running...", "failed": "FAILED", "passed": "OK"}[self.status]
        self.html_h1.text = "Status: %s" % (status,)
        self.html_h2_1.text = "[%d modules, %d suites, %d tests]" % (self.total_modules, self.total_suites, self.total_tests)
        self.html_h2_2.text = self.get_subtitle_label_for_html()
        # note that we don't use method="html" in tostring because it doesn't do indentation correctly
        # Also, we use lxml.etree instead of the Python implementation because pretty_print is not available there
        html_string = etree.tostring(self.html_root, pretty_print=True)
        try:
            html_string = str(html_string, "ascii")
        except TypeError:
            pass # python 2.x
        html_string = "<!DOCTYPE html>\n" + html_string # TODO maybe we can add the doctype with etree
        result_file = open(self.result_html_path, "w")
        result_file.write(html_string)
        result_file.close()
        self._ajax_server.trigget_refresh()
        
    def add_html_actions(self, div_elem):
        actions_span = etree.SubElement(div_elem, "span", {"class": "actions"})
        self.html_code_link = etree.SubElement(actions_span, "a", {"class": "code_link"})
        self.html_code_link.text = "C"
        span = etree.SubElement(actions_span, "span")
        span.text = " "
        self.html_desc_link = etree.SubElement(actions_span, "a", {"class": "desc_link"})
        self.html_desc_link.text = "D"
        span = etree.SubElement(actions_span, "span")
        span.text = " "
        self.html_log_link = etree.SubElement(actions_span, "a", {"class": "log_link"})
        self.html_log_link.text = "L"
    
    def add_desc(self, desc, elem):
        if desc is not None:
            desc_div = etree.SubElement(elem, "div", {"style": "display: none", "class": "description"})
            desc_div.text = desc
            self.html_desc_link.attrib["href"] = "#"
            self.html_desc_link.attrib["class"] += " minitoggle"
    
    def add_html_module(self, name, desc, code):
        self.html_module = etree.Element("div", {"class": "module"})
        module_row = etree.SubElement(self.html_module, "div", {"class": "module-row"})
        self.add_html_actions(module_row)
        self.html_module_span = etree.SubElement(module_row, "span", {"class": "module_name"})
        toggle_a = etree.SubElement(self.html_module_span, "a", {"href": "#", "class": "toggle down-arrow"})
        toggle_a.text = ""
        span = etree.SubElement(self.html_module_span, "span")
        span.text = " "
        module_text = etree.SubElement(self.html_module_span, "span")
        module_text.text = name
        self.add_desc(desc, module_row)
        if code is not None:
            self.html_code_link.attrib["href"] = code
        self.update_html()
        
    def add_html_suite(self, name, desc, code):
        self.html_suite = etree.Element("div", {"class": "suite"})
        suite_row = etree.SubElement(self.html_suite, "div", {"class": "suite-row"})
        self.add_html_actions(suite_row)
        self.html_suite_span = etree.SubElement(suite_row, "span", {"class": "suite_name"})
        toggle_a = etree.SubElement(self.html_suite_span, "a", {"href": "#", "class": "toggle down-arrow"})
        toggle_a.text = ""
        span = etree.SubElement(self.html_suite_span, "span")
        span.text = " "
        suite_text = etree.SubElement(self.html_suite_span, "span")
        suite_text.text = name
        self.add_desc(desc, suite_row)
        if code is not None:
            self.html_code_link.attrib["href"] = code
        self.update_html()
        
    def add_html_test(self, name, desc, code):
        self.html_test = etree.SubElement(self.html_suite, "div", {"class": "test test-row"})
        self.add_html_actions(self.html_test)
        self.html_test_span = etree.SubElement(self.html_test, "span", {"class": "test_name"})
        self.html_test_span.text = name
        self.add_desc(desc, self.html_test)
        if code is not None:
            self.html_code_link.attrib["href"] = code
        self.update_html()

    def add_html_separator_hr(self, elem):
        etree.SubElement(elem, "hr", {"class": "white-line"})

    def finalize(self, result):
        if self.status == "running":
            self.status = "failed" if (self.failed_tests > 0) else "passed"
        if self._use_ajax:
            [self.html_head.remove(ajax_script) for ajax_script in self._ajax_scripts]
            self.html_h1_parent.remove(self.html_spinner_element)
        self.update_html()
        self._ajax_server.trigger_end()
        
    def setLogger(self):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        stream = StringIO()
        format = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
        self.log_handler = logging.StreamHandler(stream)
        self.log_handler.setFormatter(format)
        self.log_stream.append(stream)
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, MyMemoryHandler):
                self.log_handler.filter = handler.filter
        root_logger.addHandler(self.log_handler)
    
    def addError(self, test, err):
        self.res[-1] = "failed"
    def addDeprecated(self, test):
        self.res[-1] = "skipped"
    def addFailure(self, test, err):
        self.res[-1] = "failed"
    def addSkip(self, test, reason):
        self.res[-1] = "skipped"
    def addSuccess(self, test):
        self.res[-1] = "passed"
    # we intercept the error for printing the trace into the log in the handle* functions and not the add*
    # functions because we need them before format* functions of the plugins are called - plugins mangle the error
    def handleError(self, test, err):
        self.trace[-1] = _exc_info_to_string(err, test)
    def handleFailure(self, test, err):
        self.trace[-1] = _exc_info_to_string(err, test)
        
    def startContext(self, context):
        if isclass(context):
            self.startSuite(context)
        else:
            self.startModule(context)
    def stopContext(self, context):
        if isclass(context):
            self.stopSuite(context)
        else:
            self.stopModule(context)
    
    def append_module(self):
        if not self.module_appended:
            if self.total_modules > 0:
                etree.SubElement(self.html_body_main, "hr", {"class": "module-separator"})
            self.html_body_main.append(self.html_module)
            self.module_appended = True
            self.total_modules += 1
            
    def append_suite(self):
        if not self.suite_appended:
            self.add_html_separator_hr(self.html_module)
            self.html_module.append(self.html_suite)
            self.suite_appended = True
            self.total_suites += 1
            
    def set_log_link(self):
        self.html_log_link.attrib["href"] = self.log_name[-1]
        self.update_html()
         
    def startX(self):
        for stream in self.log_stream:
            stream.flush()
        self.res.append("running")
        self.trace.append(None)
        logname = os.path.join(*self.name) + ".txt"
        log_path = os.path.join(self.root_dir_name, logname)
        dirname = os.path.dirname(log_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        logfile = AutoStream(log_path)
        self.log_name.append(logname)
        self.log_stream.append(logfile)
        self.log_handler.stream = self.log_stream[-1]
        self.log_stream[-1].add_callback(self.set_log_link)
        self.stdouts.append(sys.stdout)
        sys.stdout = MultiStream([self.stdouts[0], self.log_stream[-1]])
        
    def stopX(self):
        res = self.res.pop()
        if res == "running":
            res = "passed"
        trace = self.trace.pop()
        log_stream = self.log_stream.pop()
        self.log_handler.stream = self.log_stream[-1]
        self.name.pop()
        if trace is not None:
            log_stream.write(trace)
        sys.stdout = self.stdouts.pop()
        self.log_name.pop()
        return res
            
    def startModule(self, module):
        self.suite_code = "file://localhost" + module.__file__
        if self.suite_code.endswith(".pyc"):
            self.suite_code = self.suite_code[:-1]
        name = module.__name__
        desc = module.__doc__
        code = self.suite_code
        self.name.append(name)
        self.module_failed_suites = 0
        self.startX()
        self.log_stream[-1].add_callback(self.append_module)
        self.add_html_module(name, desc, code)
        self.html_module_span.attrib["class"] = "module_name module_" + self.res[-1]
        self.module_appended = False
    def stopModule(self, module):
        res = self.stopX()
        if res == "skipped":
            self.skipped_modules += 1
        elif self.module_failed_suites > 0:
            res = "failed"
        self.html_module_span.attrib["class"] = "module_name module_" + res
        self.update_html()
    def startSuite(self, suite):
        name = self.name[-1] + "." + suite.__name__
        desc = suite.__doc__
        code = self.suite_code
        self.suite_failed_tests = 0
        self.name.append(name)
        self.startX()
        self.suite_appended = False
        self.log_stream[-1].add_callback(self.append_suite)
        self.add_html_suite(name, desc, code)
        self.html_suite_span.attrib["class"] = "suite_name suite_" + self.res[-1]
    def stopSuite(self, suite):
        res = self.stopX()
        if res == "skipped":
            self.skipped_suites += 1
        elif self.suite_failed_tests > 0:
            res = "failed"
        if res == "failed":
            self.module_failed_suites += 1
        self.update_html()
        self.html_suite_span.attrib["class"] = "suite_name suite_" + res
    def startTest(self, test):
        mymeth = test.test.__getattribute__(test.test._testMethodName)
        name = test.id()
        desc = mymeth.__doc__
        #code = mymeth.im_func.func_code.co_filename
        code = self.suite_code
        self.append_module()
        self.append_suite()
        self.name.append(name)
        self.total_tests += 1
        self.add_html_separator_hr(self.html_suite)
        self.startX()
        self.add_html_test(name, desc, code)
        self.html_test_span.attrib["class"] = "test_name test_" + self.res[-1]
        self.update_html()
    def stopTest(self, test):
        res = self.stopX()
        if res == "skipped":
            self.skipped_tests += 1
        elif res == "failed":
            self.failed_tests += 1
            self.suite_failed_tests += 1
        self.html_test_span.attrib["class"] = "test_name test_" + res
        self.update_html()

