comId = "159761916"
timesleep = 1.6
import os
import ujson as json
import requests
import time
import hmac
import base64
from base64 import b64decode
import hashlib
import functools
from json_minify import json_minify
from box import tzFilter
import random
req = requests.Session()
class Client:
	def __init__(self):
		self.api = "https://service.narvii.com/api/v1"
		self.headers = {
		"NDCDEVICEID": self.device(),
		"SMDEVICEID": "b89d9a00-f78e-46a3-bd54-6507d68b343c", 
		"Accept-Language": "en-EN", 
		"Content-Type": "application/json; charset=utf-8",
		"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)", 
		"Host": "service.narvii.com",
		"Accept-Encoding": "gzip",
		"Connection": "keep_alive"
		}
		self.sid,self.userId = None,None
		
	def device(self):
		identifier = os.urandom(20)
		return ("42" + identifier.hex() + hmac.new(bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F"), b"\x42" + identifier, hashlib.sha1).hexdigest()).upper()
	
	def sig(self,data):
		return base64.b64encode(bytes.fromhex("42") + hmac.new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"), data.encode("utf-8"),hashlib.sha1).digest()).decode("utf-8")
		
	def login(self,email:str,password:str,device:str):
		data = json.dumps({"email": email, "secret": f"0 {password}", "deviceID": 
		device, "clientType": 100, "action": "normal", "timestamp": (int(time.time() * 1000))})
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/g/s/auth/login", data = data, headers = self.headers)
		if req.status_code!= 200:
			return req.json()["api:message"]
		try:self.sid, self.userId = req.json()["sid"], req.json()["account"]["uid"]
		except:pass
		return req.json()["api:message"]
	
	def join_community(self,comId:int):
		data = json.dumps({"timestamp": int(time.time() * 1000)})
		self.headers["NDC-MSG-SIG"] = self.sig(data=data)
		request = req.post(f"{self.api}/x{comId}/s/community/join?sid={self.sid}", data = data, headers = self.headers)
		return request.json()["api:message"]
	
	def send_time(self,comId:int,start:int=None,tz:int=-time.timezone // 1000,timers:list=None):
		data = {"userActiveTimeChunkList":[{"start": start, "end": int(start+300)}],"timestamp": int(time.time() *1000),"optInAdsFlags": 2147483647,"timezone": tz}
		if timers:
			data["userActiveTimeChunkList"] = timers
		data = json_minify(json.dumps(data))
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		self.headers["NDCDEVICEID"] = self.device()
		request = req.post(f"{self.api}/x{comId}/s/community/stats/user-active-time?sid={self.sid}", data = data, headers = self.headers)
		return request.json()["api:message"]
		
	def tz(self):
		return tzFilter()
		
	def run(self,email:str,password:str,device:str,comId:int):
		try:
			tzc = self.tz()
			print(f"Login[{email}] {self.login(email,password,device)}")
			print(f"join community {self.join_community(comId)}")
			for i in range(24):
				try:
					time.sleep(timesleep)
					print(f"generating coins![{i+1}][{self.send_time(comId=comId,tz=tzc,start=time.time())}]")
				except Exception as e:
					print(e)
					pass
		except Exception as e:
					print(e)
					pass
			
		
while True:
	for acc in json.load(open("acc.json")):
		email = acc["email"]
		password = acc["password"]
		device = acc["device"]
		client = Client()
		client.run(email,password,device,comId)