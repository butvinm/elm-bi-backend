#!/bin/bash

set -x

./build/main &
SERVER_PID=$!

ELM_BI_API_HOST=localhost ELM_BI_API_PORT=6969 PYTHONPATH=. pytest tests

kill $SERVER_PID
