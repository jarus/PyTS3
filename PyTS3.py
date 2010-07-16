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

class ServerQuery():
	def __init__(self, ip='127.0.0.1', query=10011):
		"""
		This class contains functions to connecting a TS3 Query Port and send command.
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
			return ('error', 10, 'Can not open a link on the port or IP')
		output = self.telnet.read_until('TS3', self.Timeout)
		if output.endswith('TS3') == False:
			return ('error', 20, 'This is not a Teamspeak Server')
		else:
			return ('error', 0, 'ok') 

	def disconnect(self):
		"""
		Close the link to the Teamspeak 3 query port
		@return: ('error', 0, 'ok')
		"""
		self.telnet.write('quit \n')
		self.telnet.close()
		return ('error', 0, 'ok')
		
	def escaping2string(self, string):
		"""
		Convert the escaping string form the TS3 Query to a human string.
		@param string: A string form the TS3 Query with ecaping.
		@type string: str
		@return: A human string with out escaping.
		"""
		string = str(string)
		string = string.replace('\/','/')
		string = string.replace('\s',' ')
		string = string.replace('\p','|')
		string = string.replace('\n','')
		string = string.replace('\r','')
		return string
	
	def string2escaping(self, string):
		"""
		Convert a human string to a TS3 Query Escaping String.
		@param string: A normal/human string.
		@type string: str
		@return: A string with escaping of TS3 Query.
		"""
		string = str(string)
		string = string.replace('/','\\/')
		string = string.replace(' ','\\s')
		string = string.replace('|','\\p')
		return string
		
	def command(self, cmd, parameter={}, option=[]):
		"""
		Send a command with paramters and options to the TS3 Query.
		@param cmd: The command who wants to send.
		@type cmd: str
		@param parameter: A dict with paramters and value. Example: sid=2 --> {'sid':'2'}  
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
		
		data = self.telnet.read_until("msg=ok", self.Timeout)
		data = data.split('error ')
		status = data[1]
		info = data[0].split('|')
		rinfo = []
		
		for i in range(0,len(info)):
			rinfo.append({}) 
			infoParser = re.finditer(r"(.*?)=(.*?)(\Z|\s)", info[i], re.I)
			for m in infoParser:
				rinfo[i][self.escaping2string(m.group(1))] = self.escaping2string(m.group(2))
		
		statusParser = re.finditer(r"(.*?)=(.*?)(\Z|\s)", status, re.I)
		status = {}
		for m in statusParser:
				status[self.escaping2string(m.group(1))] = self.escaping2string(m.group(2))
		return ('error', status['id'], status['msg'], status, rinfo) 