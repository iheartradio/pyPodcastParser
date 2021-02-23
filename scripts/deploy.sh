#!/bin/sh
export TWINE_USERNAME=aws
export TWINE_PASSWORD=`aws codeartifact get-authorization-token --domain content-platform --domain-owner 827541288795 --query authorizationToken --output text`
export TWINE_REPOSITORY_URL=https://content-platform-827541288795.d.codeartifact.us-east-1.amazonaws.com/pypi/content-platform/
# upgrading pip to resolve dependency issue
# https://travis-ci.community/t/cant-deploy-to-pypi-anymore-pkg-resources-contextualversionconflict-importlib-metadata-0-18/10494/26
pip install --upgrade pip
pip install twine
python setup.py sdist bdist_wheel
twine upload --verbose --repository pypodcastparser-ihr dist/*