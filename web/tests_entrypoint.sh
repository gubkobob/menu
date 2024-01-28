#!/bin/sh

pytest  -v tests/*
pytest --cov tests

exec "$@"