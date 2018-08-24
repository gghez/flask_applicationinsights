# flask_applicationinsights

Flask extension for Microsoft Azure Application Insights.

## Usage

Retrieve package from pypi:


Dependencies

```
pip install flask
pip install applicationinsights
```

Extension install

```
pip install flask_applicationinsights
```

### Basic

Will track all requests (succeeded or failed) to your application insight referenced by its instrumentation key.

```python
from flask import Flask
from flask_applicationinsights import ApplicationInsights

app = Flask(__name__)

insight = ApplicationInsights(instrumentation_key='<yours>')
insight.init_app(app)

@app.route('/')
def index():
    return 'HIT'

app.run()
```

## Contribution

Not open yet due to initial WIP.
