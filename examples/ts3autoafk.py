#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# Copyright (c) 2010 Christoph Heer (Christoph.Heer@googlemail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the \"Software\"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

## --- CONFIG AREA ----
TS3ServerIP = "thelabmill.de"
TS3QueryPort = "10011"
QueryLoginUsername = ""
QueryLoginPasswort = ""
ServerID = "1"

AFKChannelID = "48"
## --------------------


import PyTS3
import time

ts3 = PyTS3.ServerQuery(TS3ServerIP, TS3QueryPort)
ts3.connect()
ts3.command('login', {'client_login_name': QueryLoginUsername,
            'client_login_password': QueryLoginPasswort})
ts3.command('use', {'sid': ServerID})
ts3.command('clientupdate', {'client_nickname': 'PyTS3'})

afk = {}
print "PyTS3 AutoAFK by Christoph Heer (http://redmine.thelabmill.de)"
print "Start Daemon"
while True:
    clients = ts3.command('clientlist')
    for client in clients:
        if client["client_type"] != "0":
            break
        clientData = ts3.command('clientinfo', {'clid': client['clid']})
        if clientData['client_unique_identifier'] not in afk:
            if clientData['client_away'] == "1":
                afk[clientData['client_unique_identifier']] = client['cid']
                ts3.command('clientmove', {'clid': client['clid'],
                            'cid': AFKChannelID})

        elif clientData['client_unique_identifier'] in afk:
            if clientData['client_away'] == "0":
                ts3.command('clientmove', {'clid': client['clid'],
                            'cid': afk[clientData['client_unique_identifier']]})
                del afk[clientData['client_unique_identifier']]
    time.sleep(2)
