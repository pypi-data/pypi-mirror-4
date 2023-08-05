#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dabo
dabo.webupdate_urlbase = "http://dserver.leafe.com:5000/webupdate"
dabo.__version__ = "0.9.6"

app = dabo.dApp()
print app._checkForUpdates(True)
