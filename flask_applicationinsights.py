import datetime as dt
import json
import os
import subprocess
import threading
import time
import traceback

from applicationinsights import TelemetryClient
from applicationinsights.channel import TelemetryChannel, AsynchronousQueue, AsynchronousSender
from flask import _app_ctx_stack, current_app, Response, g, request, Request, Flask

CONFIG_KEY_INSTRUMENTATION_KEY = 'APPINSIGHTS_INSTRUMENTATION_KEY'
CONFIG_KEY_DEFAULT_REQUEST_NAME = 'APPINSIGHTS_DEFAULT_REQUEST_NAME'
CONFIG_DEFAULT_REQUEST_NAME = 'Flask'


def _extract_properties(req: Request, resp: Response):
    committish = subprocess.check_output(["git", "describe", "--always", "--abbrev=8"]).strip().decode('utf8')

    context = dict(req_remote_addr=req.remote_addr,
                   req_path=req.path,
                   req_host=req.host,
                   req_method=req.method,
                   req_query=req.query_string.decode('utf-8'),
                   req_body=req.data.decode('utf-8'),
                   req_form_data=json.dumps(req.form),
                   resp_status_code=resp.status_code,
                   current_exc_trace=traceback.format_exc() if resp.status_code == 500 else None,
                   committish=committish,
                   worker_pid=os.getpid(),
                   worker_tid=threading.get_ident()
                   )
    # Adds response content to log entry when any error occurs
    if context['resp_status_code'] >= 400:
        try:
            context['resp_content'] = resp.get_data(as_text=True)
        except Exception as e:
            context['resp_content'] = str(e)

    return context


class ApplicationInsights(object):
    def __init__(self, app: Flask = None, instrumentation_key: str = None):
        self.app = app
        if app is not None:
            self.init_app(app, instrumentation_key)
        self._properties_fillers = []
        self._measurements_fillers = []
        self._request_name = None
        self._instrumentation_key = instrumentation_key

    def init_app(self, app: Flask, instrumentation_key=None):
        instrumentation_key = instrumentation_key or self._instrumentation_key or os.environ.get(
            CONFIG_KEY_INSTRUMENTATION_KEY)
        if instrumentation_key:
            app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = instrumentation_key
        app.config.setdefault(CONFIG_KEY_DEFAULT_REQUEST_NAME, CONFIG_DEFAULT_REQUEST_NAME)

        app.teardown_appcontext(self.teardown)

        @app.errorhandler(Exception)
        def _exc_handler(e: Exception):
            self.client.track_exception(
                type=type(e),
                value=e,
                tb=e.__traceback__
            )

            return 'Internal server error', 500

        @app.before_request
        def _before():
            g.start_req_time = time.time()

        @app.after_request
        def _after(resp: Response):
            properties = _extract_properties(request, resp)
            for f in self._properties_fillers:
                properties.update(f(request, resp))

            measurements = {}
            for f in self._measurements_fillers:
                measurements.update(f(request, resp))

            req_name = self._request_name(request) if self._request_name else app.config[
                CONFIG_KEY_DEFAULT_REQUEST_NAME]
            self.client.track_request(
                req_name,
                request.path,
                success=resp.status_code < 400,
                response_code=resp.status_code,
                http_method=request.method,
                start_time=dt.datetime.fromtimestamp(g.start_req_time).isoformat(),
                duration=int(1000 * (time.time() - g.start_req_time)),
                properties=properties,
                measurements=measurements
            )
            self.client.flush()
            return resp

    def properties(self, f):
        """
        Assigns a function for properties filling.
        This function takes 2 parameters:
            - current flask request
            - current flask response
        And it should returns a dictionary of properties that should be added to each request track.
        :param f: Properties filler.
        :return: f
        """
        self._properties_fillers.append(f)
        return f

    def measurements(self, f):
        """
        Assigns a function for measurements filling.
        This function takes 2 parameters:
            - current flask request
            - current flask response
        And it should returns a dictionary of measurements that should be added to each request track.
        :param f: Measurements filler.
        :return: f
        """
        self._measurements_fillers.append(f)
        return f

    def request_name(self, f):
        """
        Defines a function returning current request name for grouping purpose in Application Insights.
        :param f:
        :return:
        """
        assert not self._request_name, 'Request name handler already defined.'

        self._request_name = f

    @property
    def client(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'appinsight_client'):
                ctx.appinsight_client = TelemetryClient(
                    current_app.config[CONFIG_KEY_INSTRUMENTATION_KEY],
                    telemetry_channel=TelemetryChannel(queue=AsynchronousQueue(AsynchronousSender()))
                )
            return ctx.appinsight_client

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'appinsight_client'):
            ctx.appinsight_client.flush()
