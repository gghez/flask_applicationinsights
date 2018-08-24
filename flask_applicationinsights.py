import datetime as dt
import os
import time

from applicationinsights import TelemetryClient
from applicationinsights.channel import TelemetryChannel, AsynchronousQueue, AsynchronousSender
from flask import _app_ctx_stack, current_app, Response, g, request

CONFIG_INSTRUMENTATION_KEY = 'APPINSIGHTS_INSTRUMENTATION_KEY'


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
            self.client.track_request('Flask',
                                      request.path,
                                      success=resp.status_code < 400,
                                      response_code=resp.status_code,
                                      http_method=request.method,
                                      start_time=dt.datetime.fromtimestamp(g.start_req_time).isoformat(),
                                      duration=int(1000 * (time.time() - g.start_req_time))
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


if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)
    insight = ApplicationInsights()
    insight.init_app(app)


    @app.route('/')
    def index():
        return 'HIT'


    app.run(debug=True)
