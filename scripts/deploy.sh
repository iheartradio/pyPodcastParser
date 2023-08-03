#!/bin/sh
export TWINE_USERNAME=aws
export TWINE_PASSWORD=`aws codeartifact get-authorization-token --domain content-platform --domain-owner 219619990026 --region us-east-1 --query authorizationToken --output text`
export TWINE_REPOSITORY_URL=`aws codeartifact get-repository-endpoint --domain content-platform --domain-owner 219619990026 --repository content-platform --region us-east-1 --format pypi --query repositoryEndpoint --output text`

# upgrading pip to resolve dependency issue
# https://travis-ci.community/t/cant-deploy-to-pypi-anymore-pkg-resources-contextualversionconflict-importlib-metadata-0-18/10494/26
pyenv exec pip install --upgrade pip
pyenv exec pip install twine
pyenv exec python setup.py sdist bdist_wheel
pyenv exec twine upload --verbose --repository pypodcastparser-ihr dist/*
