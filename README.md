# flask_applicationinsights

Flask extension for Microsoft Azure Application Insights.

## Dependencies

- flask>=1.0.2
- applicationinsights==0.11.6

## Usage

Retrieve package from pypi:

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

You can also provide instrumentation key as environment variable or flask configuration key. Key name is `APPINSIGHTS_INSTRUMENTATION_KEY`

## Contribution

Not open yet due to initial WIP.
