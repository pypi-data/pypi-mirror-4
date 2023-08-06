# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexey Loshkarev
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This project is cURL-based fork of couchdb-python by Christopher Lenz

from couchdbcurl.client import *

try:
    __version__ = __import__('pkg_resources').get_distribution('couchdb-python-curl').version
except:
    __version__ = '?'
