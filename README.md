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

Instrumentation key can be provided programmatically as well as by environment variable or flask configuration key.
Key name is `APPINSIGHTS_INSTRUMENTATION_KEY`.

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

### Advanced

You can also add custom properties or measurements to each tracked request by using special decorators.

```python
...

insight = ApplicationInsights(...)
...

@insight.properties
def custom_properties(req: Request, resp: Response):
    return {
        'req_pragma': req.headers.get('Pragma'),
        'resp_charset': resp.charset
    }
```

## Contribution

Not open yet due to initial WIP.
