import os
import unittest
from unittest.mock import patch, Mock

from flask import Flask

from flask_applicationinsights import ApplicationInsights, CONFIG_KEY_INSTRUMENTATION_KEY, \
    CONFIG_KEY_DEFAULT_REQUEST_NAME


class ConfigurationLoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        @self.app.route('/')
        def _index():
            return 'HIT'

        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = ''

    def test_init_from_ctor(self):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        insight = ApplicationInsights(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)

    def test_instrumentation_key_from_config(self):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        insight = ApplicationInsights()
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('cfgkey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_from_env(self):
        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = 'envkey'
        insight = ApplicationInsights()
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('envkey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_from_code(self):
        insight = ApplicationInsights(instrumentation_key='codekey')
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('codekey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_precedence_all(self):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = 'envkey'
        insight = ApplicationInsights(instrumentation_key='codekey')
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('codekey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_precedence_cfgenv(self):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = 'envkey'
        insight = ApplicationInsights()
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('envkey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_precedence_cfgcode(self):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        insight = ApplicationInsights(instrumentation_key='codekey')
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('codekey', insight.client.context.instrumentation_key)

    def test_instrumentation_key_precedence_envcode(self):
        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = 'envkey'
        insight = ApplicationInsights(instrumentation_key='codekey')
        insight.init_app(self.app)

        with self.app.app_context():
            self.assertIsNotNone(insight.client)
            self.assertEqual('codekey', insight.client.context.instrumentation_key)

    @patch('applicationinsights.TelemetryClient.track_request')
    def test_request_name_defaut(self, track_request_mock: Mock):
        self.app.config[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfgkey'
        self.app.config[CONFIG_KEY_DEFAULT_REQUEST_NAME] = 'cfgreqname'
        insight = ApplicationInsights()
        insight.init_app(self.app)

        c = self.app.test_client()
        r = c.get('/')

        self.assertEqual(b'HIT', r.data)
        self.assertEqual(1, track_request_mock.call_count)
        self.assertEqual('cfgreqname', track_request_mock.call_args[0][0])


class TrackingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        os.environ[CONFIG_KEY_INSTRUMENTATION_KEY] = 'cfginstrumentkey'

    @patch('applicationinsights.TelemetryClient.track_request')
    def test_request_tracking(self, track_request_mock: Mock):
        @self.app.route('/')
        def _index():
            return 'HIT'

        insight = ApplicationInsights()
        insight.init_app(self.app)

        c = self.app.test_client()
        c.get('/')

        self.assertEqual(1, track_request_mock.call_count)
        self.assertEqual(('Flask', '/'), track_request_mock.call_args[0])
        self.assertTrue(track_request_mock.call_args[1]['success'])
        self.assertEqual(200, track_request_mock.call_args[1]['properties']['resp_status_code'])
        self.assertEqual('GET', track_request_mock.call_args[1]['http_method'])
        self.assertDictEqual({}, track_request_mock.call_args[1]['measurements'])

    @patch('applicationinsights.TelemetryClient.track_request')
    def test_request_tracking_request_name(self, track_request_mock: Mock):
        @self.app.route('/')
        def _index():
            return 'HIT'

        insight = ApplicationInsights()
        insight.init_app(self.app)

        @insight.request_name
        def _request_name(req):
            return 'AnotherRequestGroup'

        c = self.app.test_client()
        c.get('/')

        self.assertEqual(1, track_request_mock.call_count)
        self.assertEqual(('AnotherRequestGroup', '/'), track_request_mock.call_args[0])

    @patch('applicationinsights.TelemetryClient.track_request')
    def test_request_tracking_with_properties(self, track_request_mock: Mock):
        @self.app.route('/')
        def _index():
            return 'HIT'

        insight = ApplicationInsights()
        insight.init_app(self.app)

        @insight.properties
        def _properties(req, resp):
            return {
                'prop1': 4,
                'prop2': 'string'
            }

        c = self.app.test_client()
        c.get('/')

        self.assertEqual(1, track_request_mock.call_count)
        self.assertEqual(4, track_request_mock.call_args[1]['properties']['prop1'])
        self.assertEqual('string', track_request_mock.call_args[1]['properties']['prop2'])

    @patch('applicationinsights.TelemetryClient.track_request')
    def test_request_tracking_with_measurements(self, track_request_mock: Mock):
        @self.app.route('/')
        def _index():
            return 'HIT'

        insight = ApplicationInsights()
        insight.init_app(self.app)

        @insight.measurements
        def _measurements(req, resp):
            return {
                'm1': 4.9,
                'm2': 5.1
            }

        c = self.app.test_client()
        c.get('/')

        self.assertEqual(1, track_request_mock.call_count)
        self.assertEqual(4.9, track_request_mock.call_args[1]['measurements']['m1'])
        self.assertEqual(5.1, track_request_mock.call_args[1]['measurements']['m2'])

    @patch('applicationinsights.TelemetryClient.track_exception')
    def test_exception_tracking(self, track_exception_mock: Mock):
        @self.app.route('/error')
        def _error():
            raise Exception('Fake exception')

        insight = ApplicationInsights()
        insight.init_app(self.app)

        c = self.app.test_client()
        c.get('/error')

        self.assertEqual(1, track_exception_mock.call_count)
        self.assertEqual(Exception, track_exception_mock.call_args[1]['type'])
        self.assertEqual('Fake exception', track_exception_mock.call_args[1]['value'].args[0])


if __name__ == '__main__':
    unittest.main()
