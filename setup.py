"""
Flask-ApplicationInsights
-------------

Microsoft Azure Application Insights integration for Flask.
"""
from setuptools import setup


setup(
    name='Flask-ApplicationInsights',
    version='1.0',
    url='http://example.com/flask-sqlite3/',
    license='BSD',
    author='Gregory ghez',
    author_email='gregory.ghez@gmail.com',
    description='Microsoft Azure Application Insights integration for Flask.',
    long_description=__doc__,
    py_modules=['flask_applicationinsights'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)