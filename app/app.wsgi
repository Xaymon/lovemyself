#!/usr/bin/python
# coding: utf-8

import sys
import gunicorn.app.base
import gunicorn.util

sys.path.append('/home/flask')

from app import app as application
