import random
import time

from flask import Flask

from flask_applicationinsights import ApplicationInsights

demo = Flask(__name__)
insight = ApplicationInsights()
insight.init_app(demo)


@demo.route('/')
def index():
    time.sleep(random.random())
    return 'HIT'


demo.run(debug=True)
