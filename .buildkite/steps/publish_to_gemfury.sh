#!/bin/bash

NAME=$(python setup.py --name)
VERSION=$(python setup.py --version)
SDIST=dist/${NAME}-${VERSION}.tar.gz

buildkite-agent artifact download dist/*.tar.gz ./ && \
curl -f -F package=@${SDIST} ${GEMFURY_URL}
