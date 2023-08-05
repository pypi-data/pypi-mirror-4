# -*- coding: utf-8 -*-

import httplib,json,sys,traceback
from base64 import b64decode,b64encode

DEBUG_JSONLIB=False

class JSONRemoteMethod:
	def __init__(self,methodName,transport):
		self._methodName = methodName
		self._transport = transport
	def __call__(self, *args):
		#print "args:",args,len(args)
		#print "self._methodName:",self._methodName
		req = { 'method':self._methodName, 'params':args }
		return self._transport.sendRequest(req)
	def __getattr__(self,name):
		if self.__dict__.has_key(name) or name.startswith("_"):
			#print "CE L'HO",name
			return self.__dict__[name]
		self._methodName = "%s.%s" %(self._methodName,name)
		return self

class Binary:
	def __init__(self,payload):
		self._payload = payload
	def __str__(self):
		if (type(self._payload)==str or type(self._payload)==unicode) and self._payload.startswith("base64:"):
			return b64decode( self._payload[len("base64:"):] )
		return "base64:%s" % b64encode(self._payload)

class JSONServer:
	def __init__(self, host, transport=None, SESSION_ID_STRING='PHPSESSID'):
		self._protocol , tmp = host.split("://")
		tmp = tmp.split("/")
		self._host = tmp[0]
		self._port = 80
		if self._host.find(":")>=0:
			tmp2 = self._host.split(":")
			self._host = tmp2[-2]
			self._port = tmp2[-1]
		self._uri = "/%s" % "/".join(tmp[1:])
		if DEBUG_JSONLIB:
			print "JSONServer.__init__: self._protocol:",self._protocol
			print "JSONServer.__init__: self._host:",self._host
			print "JSONServer.__init__: self._port:",self._port
			print "JSONServer.__init__: self._uri:",self._uri
		self._transport=transport
		self._reqMethod="POST"
		self.mycookies=None
		self.mysessid=None
		self.SESSION_ID_STRING = SESSION_ID_STRING
		self._reqId = 0

	def __getattr__(self,name):
		if self.__dict__.has_key(name) or name.startswith("_"):
			#print "CE L'HO",name
			return self.__dict__[name]
		return JSONRemoteMethod(name,self)
	def sendRequest(self,req):
		req['id'] = self._reqId
		self._reqId += 1
		json_req = json.dumps(req)
		conn = httplib.HTTPConnection(self._host)
		req_body=json_req
		req_headers={}
		if not self.mysessid is None:
			req_headers["Cookie"] = "%s=%s" % (self.SESSION_ID_STRING,self.mysessid)
		conn.request(self._reqMethod, self._uri, req_body, req_headers)
		r1 = conn.getresponse()
		#print r1.status, r1.reason
		data1 = r1.read()
		#print dir(r1)
		headers = r1.getheaders()
		#print dir(headers)
		for h in headers:
			#print "h:",h
			nome,valore = h
			if nome=='set-cookie':
				self.mycookies = self.parseCookies(valore)
				if self.mysessid is None:
					if self.mycookies.has_key(self.SESSION_ID_STRING):
						self.mysessid = self.mycookies[self.SESSION_ID_STRING]
		conn.close()
		if DEBUG_JSONLIB: print "JSONServer.sendRequest: data1=%s"%data1
		try:
			return json.loads(data1)
		except Exception,e:
			print "JSONServer.sendRequest: ECCEZIONE ############# Inizio."
			print "ECCEZIONE: %s" % ( e )
			print "".join( traceback.format_tb(sys.exc_info()[2]) )
			print "JSONServer.sendRequest: ECCEZIONE ############# Data"
			print data1
			print "JSONServer.sendRequest: ECCEZIONE ############# Fine."
	def test(self):
		conn = httplib.HTTPConnection(self._host)
		#print "conn:",conn
		req_body=""
		req_headers={}
		if not self.mysessid is None:
			req_headers["Cookie"] = "%s=%s" % (self.SESSION_ID_STRING,self.mysessid)
		conn.request("GET", self._uri, req_body, req_headers)
		r1 = conn.getresponse()
		#print r1.status, r1.reason
		data1 = r1.read()
		#print dir(r1)
		headers = r1.getheaders()
		#print dir(headers)
		for h in headers:
			#print "h:",h
			nome,valore = h
			if nome=='set-cookie':
				self.mycookies = self.parseCookies(valore)
				if self.mysessid is None:
					if self.mycookies.has_key(self.SESSION_ID_STRING):
						self.mysessid = self.mycookies[self.SESSION_ID_STRING]
		conn.close()
		print "self.mycookies:",self.mycookies
		return data1
	def parseCookies(self,s):
		if s is None: return {self.SESSION_ID_STRING:None}
		ret = {}
		tmp = s.split(';')
		for t in tmp:
			coppia = t.split('=')
			k = coppia[0].strip()
			v = coppia[1].strip()
			ret[k]=v
		return ret

if __name__=='__main__':
	import sys
	s = None
	if sys.platform=='darwin':
		s = JSONServer("http://localhost/~robertoroccoangeloni/rproject/plugins/jsonserver/jsonserver.php")
	else:
		s = JSONServer("http://localhost/~roberto/rproject/plugins/jsonserver/jsonserver.php")
	#print s.test()
	#print "s.mycookies:",s.mycookies
	print "ping:",s.ping()
	#print "s.mycookies:",s.mycookies
	print "echo:",s.echo("cippa",123.4,False,u"Lippà")
	#print "s.mycookies:",s.mycookies
	print "login:",s.login('roberto','echoestrade')
	#print "s.mycookies:",s.mycookies
	print "dbmgr.db_version():",s.dbmgr.db_version()
	print "dbmgr.getDBEUser():",s.dbmgr.getDBEUser()
	print "dbmgr.getUserGroupsList():",s.dbmgr.getUserGroupsList()

