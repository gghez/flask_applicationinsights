"""
Flask-ApplicationInsights
-------------

Microsoft Azure Application Insights integration for Flask.
"""
from setuptools import setup


setup(
    name='Flask-ApplicationInsights',
    version='0.1.0',
    url='https://github.com/gghez/flask_applicationinsights',
    license='MIT',
    author='Gregory Ghez',
    author_email='gregory.ghez@gmail.com',
    description='Microsoft Azure Application Insights integration for Flask.',
    long_description=__doc__,
    py_modules=['flask_applicationinsights'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=1.0.2',
        'applicationinsights==0.11.6'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)