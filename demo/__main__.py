import random
import time

from flask import Flask, Request, Response

from flask_applicationinsights import ApplicationInsights

demo = Flask(__name__)
insight = ApplicationInsights()
insight.init_app(demo)


@demo.route('/')
def index():
    time.sleep(random.random())
    return 'HIT'


@demo.route('/other')
def other():
    time.sleep(random.random())
    return 'HIT'


@demo.route('/error')
def error():
    raise Exception('Ole')


@insight.request_name
def request_name(req: Request):
    if req.path == '/other':
        return 'Other'
    return 'Flask'


@insight.properties
def custom_properties(req: Request, resp: Response):
    return {
        'req_pragma': req.headers.get('Pragma'),
        'resp_charset': resp.charset
    }


demo.run(debug=True)
