#!/bin/sh

RPCDIR=
AGENT_SOCKET=
SERVER_SOCKET=
BUNDLE=
ENVDIR=

rm -fr ${ENVDIR}
virtualenv --no-site-packages ${ENVDIR}
pip install -E ${ENVDIR} --upgrade ${BUNDLE}
