#!/bin/bash

gunicorn -w 1 -b "0.0.0.0:9002" app:app
