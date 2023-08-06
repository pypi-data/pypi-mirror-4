import urllib, urllib2
import json as json
import hashlib

#
# REAKTOR
#
class Reaktor:

	# 
	# INIT
	#
	# constructor with log in of reaktor.io service
	def __init__(self, mail, password):

		# login to reaktor.io
		self.__api = "http://api.reaktor.io/"
		
		d = {
			"mail"  : mail, 
			"pass"  : hashlib.md5(password).hexdigest(),
			"client": "py"
		}

		# create POST request to login
		req = urllib2.urlopen(self.__api + "login", urllib.urlencode(d))

		# get result object
		res = json.loads(req.read())

		# validate result of login
		if bool(res["ok"]) == True:
			self.__token = res["token"]
		else:
			raise Exception(res["reason"])


	# 
	# TRIGGER
	#
	# triggers an reaktor.io event by its name
	#
	# name: the name of the event in reaktor.io system
	# data: the data object to fill in the variables in template
	# save: (optional) waits till event is triggered and returns a 
	#		boolean of its status. default is False, so the event will 
	# 		be triggered asyncroniously and returns True
	#
	def trigger(self, name, data=None, safe=False):

		d = {
			"token" : self.__token,
			"name"  : name, 
			"safe"  : safe,
			"client": "py"
		}

		# if specified append data object
		if data: d["data"] = data

		req = urllib2.Request(self.__api + "trigger", json.dumps(d), {"Content-Type": "application/json"})
		f = urllib2.urlopen(req)
		res = json.loads(f.read())
		f.close()

		# validate result
		if bool(res["ok"]) == True:
			return True

		else:
			# if safe mode is on, throw exeption 
			if safe: raise Exception(res["reason"])
			return False