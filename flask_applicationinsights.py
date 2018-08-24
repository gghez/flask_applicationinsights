import datetime as dt
import json
import os
import subprocess
import threading
import time
import traceback

from applicationinsights import TelemetryClient
from applicationinsights.channel import TelemetryChannel, AsynchronousQueue, AsynchronousSender
from flask import _app_ctx_stack, current_app, Response, g, request, Request

CONFIG_INSTRUMENTATION_KEY = 'APPINSIGHTS_INSTRUMENTATION_KEY'


def _extract_properties(req: Request, resp: Response):
    committish = subprocess.check_output(["git", "describe", "--always", "--abbrev=8"]).strip().decode('utf8')

    context = dict(req_remote_addr=req.remote_addr,
                   req_path=req.path,
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
    def __init__(self, app=None, instrumentation_key=None):
        self.app = app
        if app is not None:
            self.init_app(app, instrumentation_key)

    def init_app(self, app, instrumentation_key=None):
        instrumentation_key = instrumentation_key or os.environ.get(CONFIG_INSTRUMENTATION_KEY)
        app.config.setdefault(CONFIG_INSTRUMENTATION_KEY, instrumentation_key)
        app.teardown_appcontext(self.teardown)

        def _before():
            g.start_req_time = time.time()

        def _after(resp: Response):
            self.client.track_request(
                'Flask',
                request.path,
                success=resp.status_code < 400,
                response_code=resp.status_code,
                http_method=request.method,
                start_time=dt.datetime.fromtimestamp(g.start_req_time).isoformat(),
                duration=int(1000 * (time.time() - g.start_req_time)),
                properties=_extract_properties(request, resp)
            )
            self.client.flush()
            return resp

        app.before_request(_before)
        app.after_request(_after)

    @property
    def client(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'appinsight_client'):
                ctx.appinsight_client = TelemetryClient(
                    current_app.config[CONFIG_INSTRUMENTATION_KEY],
                    telemetry_channel=TelemetryChannel(queue=AsynchronousQueue(AsynchronousSender()))
                )
            return ctx.appinsight_client

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'appinsight_client'):
            ctx.appinsight_client.flush()
