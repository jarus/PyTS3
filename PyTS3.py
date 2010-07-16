#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Christoph Heer (Christoph.Heer@googlemail.com)
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

import telnetlib
import re
import thread
import time


class TS3Error(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "ID %s (%s)" % (self.code, self.msg)


class ServerQuery():
    TSRegex = re.compile(r"(\w+)=(.*?)(\s|$|\|)")

    def __init__(self, ip='127.0.0.1', query=10011):
        """
        This class contains functions to connecting a TS3 Query Port and send
        command.
        @param ip: IP adress of the TS3 Server
        @type ip: str
        @param query: Query Port of the TS3 Server. Default 10011
        @type query: int
        """
        self.IP = ip
        self.Query = int(query)
        self.Timeout = 5.0

    def connect(self):
        """
        Open a link to the Teamspeak 3 query port
        @return: A tulpe with a error code. Example: ('error', 0, 'ok')
        """
        try:
            self.telnet = telnetlib.Telnet(self.IP, self.Query)
        except telnetlib.socket.error:
            raise TS3Error(10, 'Can not open a link on the port or IP')
        output = self.telnet.read_until('TS3', self.Timeout)
        if output.endswith('TS3') == False:
            raise TS3Error(20, 'This is not a Teamspeak 3 Server')
        else:
            return True

    def disconnect(self):
        """
        Close the link to the Teamspeak 3 query port
        @return: ('error', 0, 'ok')
        """
        self.telnet.write('quit \n')
        self.telnet.close()
        return True

    def escaping2string(self, string):
        """
        Convert the escaping string form the TS3 Query to a human string.
        @param string: A string form the TS3 Query with ecaping.
        @type string: str
        @return: A human string with out escaping.
        """
        string = str(string)
        string = string.replace('\/', '/')
        string = string.replace('\s', ' ')
        string = string.replace('\p', '|')
        string = string.replace('\n', '')
        string = string.replace('\r', '')
        try:
            string = int(string)
            return string
        except ValueError:
            ustring = unicode(string, "utf-8")
            return ustring

    def string2escaping(self, string):
        """
        Convert a human string to a TS3 Query Escaping String.
        @param string: A normal/human string.
        @type string: str
        @return: A string with escaping of TS3 Query.
        """
        if type(string) == type(int()):
            string = str(string)
        else:
            string = string.encode("utf-8")
            string = string.replace('/', '\\/')
            string = string.replace(' ', '\\s')
            string = string.replace('|', '\\p')
        return string

    def command(self, cmd, parameter={}, option=[]):
        """
        Send a command with paramters and options to the TS3 Query.
        @param cmd: The command who wants to send.
        @type cmd: str
        @param parameter: A dict with paramters and value.
        Example: sid=2 --> {'sid':'2'}
        @type cmd: dict
        @param option: A list with options. Example: –uid --> ['uid']
        @type option: list
        @return: The answer of the server as tulpe with error code and message.
        """
        telnetCMD = cmd
        for key in parameter:
            telnetCMD += " %s=%s" % (key, self.string2escaping(parameter[key]))
        for i in option:
            telnetCMD += " -%s" % (i)
        telnetCMD += '\n'
        self.telnet.write(telnetCMD)

        telnetResponse = self.telnet.read_until("msg=ok", self.Timeout)
        telnetResponse = telnetResponse.split(r'error id=')
        notParsedCMDStatus = "id=" + telnetResponse[1]
        notParsedInfo = telnetResponse[0].split('|')

        if (cmd.endswith("list") == True) or (len(notParsedInfo) > 1):
            returnInfo = []
            for notParsedInfoLine in notParsedInfo:
                ParsedInfo = self.TSRegex.findall(notParsedInfoLine)
                ParsedInfoDict = {}
                for ParsedInfoKey in ParsedInfo:
                    ParsedInfoDict[ParsedInfoKey[0]] = self.escaping2string(
                        ParsedInfoKey[1])
                returnInfo.append(ParsedInfoDict)

        else:
            returnInfo = {}
            ParsedInfo = self.TSRegex.findall(notParsedInfo[0])
            for ParsedInfoKey in ParsedInfo:
                returnInfo[ParsedInfoKey[0]] = self.escaping2string(
                    ParsedInfoKey[1])

        ReturnCMDStatus = {}
        ParsedCMDStatus = self.TSRegex.findall(notParsedCMDStatus)
        for ParsedCMDStatusLine in ParsedCMDStatus:
            ReturnCMDStatus[ParsedCMDStatusLine[0]] = self.escaping2string(
                ParsedCMDStatusLine[1])
        if ReturnCMDStatus['id'] != 0:
            raise TS3Error(ReturnCMDStatus['id'], ReturnCMDStatus['msg'])

        return returnInfo


class ServerNotification(ServerQuery):
    def __init__(self, ip='127.0.0.1', query=10011):
        """
        This class contains functions to work with the
        ServerNotification of TS3.
        @param ip: IP adress of the TS3 Server
        @type ip: str
        @param query: Query Port of the TS3 Server. Default 10011
        @type query: int
        """
        self.IP = ip
        self.Query = int(query)
        self.Timeout = 5.0
        self.LastCommand = 0

        self.Lock = thread.allocate_lock()
        self.RegistedNotifys = []
        self.RegistedEvents = []
        thread.start_new_thread(self.worker, ())

    def worker(self):
        while True:
            self.Lock.acquire()
            RegistedNotifys = self.RegistedNotifys
            LastCommand = self.LastCommand
            self.Lock.release()
            if len(RegistedNotifys) == 0:
                continue
            if LastCommand < time.time() - 180:
                self.command('version')
                self.Lock.acquire()
                self.LastCommand = time.time()
                self.Lock.release()
            telnetResponse = self.telnet.read_until("\n", 0.1)
            if telnetResponse.startswith('notify'):
                notifyName = telnetResponse.split(' ')[0]
                ParsedInfo = self.TSRegex.findall(telnetResponse)
                notifyData = {}
                for ParsedInfoKey in ParsedInfo:
                    notifyData[ParsedInfoKey[0]] = self.escaping2string(
                        ParsedInfoKey[1])
                for RegistedNotify in RegistedNotifys:
                    if RegistedNotify['notify'] == notifyName:
                        RegistedNotify['func'](notifyName, notifyData)
            time.sleep(0.2)

    def registerNotify(self, notify, func):
        notify2func = {'notify': notify, 'func': func}

        self.Lock.acquire()
        self.RegistedNotifys.append(notify2func)
        self.LastCommand = time.time()
        self.Lock.release()

    def unregisterNotify(self, notify, func):
        notify2func = {'notify': notify, 'func': func}

        self.Lock.acquire()
        self.RegistedNotifys.remove(notify2func)
        self.LastCommand = time.time()
        self.Lock.release()

    def registerEvent(self, eventName, parameter={}, option=[]):
        parameter['event'] = eventName
        self.RegistedEvents.append(eventName)
        self.command('servernotifyregister', parameter, option)
        self.Lock.acquire()
        self.LastCommand = time.time()
        self.Lock.release()

    def unregisterEvent(self):
        self.command('servernotifyunregister')
