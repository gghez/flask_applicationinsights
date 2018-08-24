"""
Flask-ApplicationInsights
-------------

Microsoft Azure Application Insights integration for Flask.
"""
import subprocess

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-ApplicationInsights',
    version=subprocess.check_output(["git", "describe", "--always", "--tags"]).strip().decode('utf8'),
    url='https://github.com/gghez/flask_applicationinsights',
    license='MIT',
    author='Gregory Ghez',
    author_email='gregory.ghez@gmail.com',
    description='Microsoft Azure Application Insights integration for Flask.',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
