#!/usr/bin/env bash

python setup.py test

echo -n "New version: "
read VERSION

[[ ${VERSION} =~ ^[0-9]\.[0-9]\.[0-9]$ ]] || exit 1

git tag -a ${VERSION} -m "Release ${VERSION}"
git push --tags

rm -fr build dist Flask_ApplicationInsights.egg-info

python setup.py sdist bdist_wheel upload
