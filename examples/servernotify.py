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
ServerID = "1"
## --- CONFIG AREA ----

import time
import PyTS3


## First we create a Function, it is called at a notify.
## A NotifyPrinter Func has 2 args:
## 1. NotifyName (str)
## 2. NotifyData (dict)
## In this example the function show the name and the data
def notifyPrinter(name, data):
    print "New Notify: %s" % (name)
    print data


## Now we create the Main Application
def main():
    print "Example of the PyTS3 ServerNotification Class"
    ## We create a instance of PyTS3.ServerNotification with IP and QueryPort
    ts3 = PyTS3.ServerNotification(TS3ServerIP, TS3QueryPort)
    ## After the Init, we has a new thread, the worker, it read the input form
    ## the server. ServerNotification has all functions of ServerQuery but use
    ## only this Class for Notifycations

    ## We connect
    ts3.connect()
    ## Now we select a server
    ts3.command('use', {'sid': ServerID})

    ## After this we register events, which we can do with the function
    ## registerEvent(self, eventName, parameter={}, option=[])
    ts3.registerEvent('server')
    ## You can add later other events too

    ## Now we register the notifiy and the function which is work with this
    ts3.registerNotify('notifycliententerview', notifyPrinter)
    ## the first para is the name of the notify the secound is the function
    ## which get the notify data

    ## Now we start a loop and wait for events or other task
    while True:
        time.sleep(0.5)

    ## When a the worker found a new notify than he call the function
    ## notifyPrinter and we can see the NotifyName and the Data

if __name__ == '__main__':
    main()
