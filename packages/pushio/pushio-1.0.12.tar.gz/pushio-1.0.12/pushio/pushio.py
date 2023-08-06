#!/usr/bin/env python
# encoding: utf-8
"""
pushio.py

Copyright (c) 2012-2013 Push IO Inc. All rights reserved.
"""

import sys
import os
import urllib
import json
import csv
import datetime

PUSHIO_API_ENDPOINT = "https://manage.push.io"
PUSHIO_API_VERSION = "v1"

class API:
	def __init__(self, appID, senderSecret, customEndpoint=None, debug=False):
		"""This is the object that you should create to send API requests to Push IO"""
		
		if appID == None or len(appID) == 0 or \
			senderSecret == None or len(senderSecret) == 0 or \
			appID == "Your App ID" or senderSecret == "Your Sender Secret":
			raise Exception("You must initialize this class with your App ID and Sender Secret")
		
		self.appID = appID
		self.senderSecret = senderSecret
		
		self.customEndpoint = customEndpoint
		self.debug = debug
					
	def sendBroadcastPushNotification(self, notification, dedup_key=None, deliver_at=None, not_after=None):
		params = {
			"payload" : notification.json,
			"audience" : "broadcast"
		}
		
		if dedup_key is not None:
			params["dedup_key"] = dedup_key
			
		if deliver_at is not None:
			params["deliver_at"] = deliver_at
			
		if not_after is not None:
			params["not_after"] = not_after
							
		self.post("notify_app", params)
		
	def sendTestDevicePushNotification(self, notification, dedup_key=None, deliver_at=None, not_after=None):
		params = {
			"payload" : notification.json,
		}
		
		if dedup_key is not None:
			params["dedup_key"] = dedup_key
			
		if deliver_at is not None:
			params["deliver_at"] = deliver_at
			
		if not_after is not None:
			params["not_after"] = not_after
			
		self.post("test_app", params)

	def sendCategoryPushNotification(self, notification, categories, dedup_key=None, deliver_at=None, not_after=None):
		params = {
			"payload" : notification.json,
			"tag_query" : categories
		}
		
		if dedup_key is not None:
			params["dedup_key"] = dedup_key
			
		if deliver_at is not None:
			params["deliver_at"] = deliver_at
			
		if not_after is not None:
			params["not_after"] = not_after
			
		self.post("notify_app", params)
		
	def sendNewsstandContentAvailablePushNotification(self, dedup_key=None, deliver_at=None, not_after=None):
		apns = APNS(aps_extra={"content-available":1})
		notification = Notification(payload_apns=apns.payload)
		
		params = {
			"payload" : notification.json,
			"audience" : "broadcast"
		}
		
		if dedup_key is not None:
			params["dedup_key"] = dedup_key
			
		if deliver_at is not None:
			params["deliver_at"] = deliver_at
			
		if not_after is not None:
			params["not_after"] = not_after
			
		self.post("notify_app", params)
			
	def getNotifications(self, offset=None, limit=None, apiKey=None):
		params = {
		}

		if offset:
			params["offset"] = offset

		if limit:
			params["limit"] = limit

		encodedParams = urllib.urlencode(params)

		jsonData = self.get("notifications", encodedParams, "json", apiKey=apiKey)
		return jsonData
		
	def getCategories(self, offset=None, limit=None, apiKey=None):
		params = {
		}

		if offset:
			params["offset"] = offset

		if limit:
			params["limit"] = limit

		encodedParams = urllib.urlencode(params)

		jsonData = self.get("categories", encodedParams, "json", apiKey=apiKey)
		return jsonData

	def endpoint(self, handler, fileType=None, apiKey=None):
		extension = ""
		if fileType:
			extension = ".%s" %(fileType)
			
		if self.customEndpoint:
			apiURL = self.customEndpoint
		else:
			apiURL = PUSHIO_API_ENDPOINT
			
		if apiKey:
			if handler is "notifications" or "categories":
				apiString = "%s/api/%s/%s/%s/%s%s" %(apiURL, PUSHIO_API_VERSION, apiKey,self.senderSecret, handler, extension)
			else:
				apiString = "%s/api/%s/%s/%s/%s%s" %(apiURL, PUSHIO_API_VERSION, handler, apiKey, self.senderSecret, extension)
		else:
			if handler is "notifications" or "categories":
				apiString = "%s/api/%s/%s/%s/%s%s" %(apiURL, PUSHIO_API_VERSION, self.appID, self.senderSecret, handler, extension)
			else:
				apiString = "%s/api/%s/%s/%s/%s%s" %(apiURL, PUSHIO_API_VERSION, handler, self.appID,self.senderSecret, extension)
		
		return apiString
		
	def get(self, handler, params, fileType=None, apiKey=None):
		jsonData = None
		endpoint = "%s?%s" %(self.endpoint(handler, fileType=fileType, apiKey=apiKey), params)
		status = urllib.urlopen(endpoint)
		if status.code == 200:
			jsonData = json.load(status)
			
			if self.debug == True:
				print "===Push IO API response==="
				print "%d success" %(status.code)
		else:
			print "===Push IO API response==="
			print "%d failure" %(status.code)
				
		return jsonData
					
	def post(self, handler, params):
		endpoint = self.endpoint(handler)
		encodedParams = urllib.urlencode(params)
		
		if self.debug == True:
			print "===Push IO API request==="
			print "URL: %s" %(endpoint)	
			print "Params: %s\n" %(encodedParams)
		
		status = urllib.urlopen(endpoint, encodedParams)
		if status.code == 201:
			if self.debug == True:
				print "===Push IO API response==="
				print "%d success" %(status.code)
				print status.read()
		else:
			print "===Push IO API response==="
			print "%d failure" %(status.code)
			print status.read()

	def secondsFromNow(self, seconds):
		secs = float(seconds)
		import time
		t = time.time()
		t2 = t + secs

		gmtTime = time.gmtime(t2)
		gmtTimeISO8601 = time.strftime('%Y-%m-%dT%H:%M:%SZ', gmtTime)

		return gmtTimeISO8601
		
class Notification:
	def __init__(self, message=None, extra=None, payload_apns=None, payload_gcm=None, payload_mpns=None):
		self.payload = {}
		
		if message:
			self.payload["message"] = message
		if extra:
			self.payload["extra"] = extra
		if payload_apns:
			self.payload["payload_apns"] = payload_apns
		if payload_gcm:
			self.payload["payload_gcm"] = payload_gcm
		if payload_mpns:
			self.payload["payload_mpns"] = payload_mpns
				
		self.json = json.dumps(self.payload)
		
		
class APNS:
	def __init__(self, alert=None, badge=None, sound=None, extra=None, aps_extra=None):
		self.payload = {}
		
		if alert:
			self.payload["alert"] = alert
		if badge:
			self.payload["badge"] = badge
		if sound:
			self.payload["sound"] = sound
		if extra:
			self.payload["extra"] = extra
		if aps_extra:
			self.payload["aps_extra"] = aps_extra
				
class GCM:
	def __init__(self, alert=None, badge=None, sound=None, extra=None, collapse_key=None, delay_while_idle=None, time_to_live=None):
		self.payload = {}
		
		if alert:
			self.payload["alert"] = alert
		if badge:
			self.payload["badge"] = badge
		if sound:
			self.payload["sound"] = sound
		if extra:
			self.payload["extra"] = extra
		if collapse_key:
			self.payload["collapse_key"] = collapse_key
		if delay_while_idle:
			self.payload["delay_while_idle"] = delay_while_idle
		if time_to_live:
			self.payload["time_to_live"] = time_to_live
		
class MPNS:
	def __init__(self, toast_text1=None, \
						toast_text2=None, 
						tile_id=None, \
						tile_count=None, \
						tile_title=None, \
						tile_background_image=None, \
						tile_back_title=None, \
						tile_back_background_image=None, \
						tile_back_content=None, \
						props_to_clear=None, toast=None):
		self.payload = {}
		
		if toast_text1:
			self.payload["toast_text1"] = toast_text1
		if toast_text2:
			self.payload["toast_text2"] = toast_text2
		if tile_id:
			self.payload["tile_id"] = tile_id
		if tile_count:
			self.payload["tile_count"] = tile_count
		if tile_title:
			self.payload["tile_title"] = tile_title
		if tile_background_image:
			self.payload["tile_background_image"] = tile_background_image
		if tile_back_title:
			self.payload["tile_back_title"] = tile_back_title
		if tile_back_background_image:
			self.payload["tile_back_background_image"] = tile_back_background_image
		if tile_back_content:
			self.payload["tile_back_content"] = tile_back_content
		if props_to_clear:
			self.payload["props_to_clear"] = props_to_clear
		if toast:
			self.payload["toast"] = toast
		
class NotificationReporter:

	def __init__(self, apiObject, limit=None, offset=None, apiKey=None, query=False):
		self.notificationList = []
		self.query=query
		
		if apiObject:
			notifications = apiObject.getNotifications(limit=limit, offset=offset, apiKey=apiKey)
						
			if notifications:
				for n in notifications:
					notification = {}

					if "timestamp" in n:
						timeStamp = n["timestamp"]
						dateTime = datetime.datetime.fromtimestamp(timeStamp / 1e3).strftime("%Y-%m-%d %H:%M:%S UTC")
						notification["dateTime"] = dateTime
						
					if "plats" in n:
						plats = n["plats"].split(",")				        
				
					if "abstract" in n:
						notification["message"] = n["abstract"]		

					if "delivery_count" in n:
						notification["deliveries"] = n["delivery_count"]
						
					if "active_engagements" in n:
						notification["active_engagements"] = n["active_engagements"]
					
					if "launch_engagements" in n:
						notification["launch_engagements"] = n["launch_engagements"]			

					if "total_engagements" in n:
						notification["total_engagements"] = n["total_engagements"]		
						
					if query == True and "tag_query" in n:
						notification["query"] = n["tag_query"]	

					self.notificationList.append(notification)

	def outputToCSV(self, fileName):
		f = open(fileName, 'w')
		csvFile = csv.writer(f)
		
		if self.query == True:
			csvFile.writerow(["Date", "Message", "Query", "Pushes Sent", "User Engagement %", "Launch Engagements", "Active Engagements", "Total Engagements"])
		else:
			csvFile.writerow(["Date", "Message", "Pushes Sent", "User Engagement %", "Launch Engagements", "Active Engagements", "Total Engagements"])
		
		for n in self.notificationList: 
			total = 0
			launch = 0
			active = 0
			pushesSent = 0
			engagementRate = 0
			
			if "total_engagements" in n:
				total = n["total_engagements"]

			if "launch_engagements" in n:
				launch = n["launch_engagements"]
			
			if "active_engagements" in n:
				active = n["active_engagements"]
									
			if "deliveries" in n:
				pushesSent = n["deliveries"]
				if pushesSent > 0:
					engagementRate = (total / float(pushesSent)) * 100
					
			if self.query == True:
				csvFile.writerow([n["dateTime"], n["message"], n["query"], pushesSent, engagementRate, launch, active, total])
			else:
				csvFile.writerow([n["dateTime"], n["message"], pushesSent, engagementRate, launch, active, total])
				
		f.close()
		
class CategoryReporter:

	def __init__(self, apiObject, limit=None, offset=None, apiKey=None):
		if apiObject:
			self.categoryList = apiObject.getCategories(limit=limit, offset=offset, apiKey=apiKey)
			
	def outputToCSV(self, fileName):
		f = open(fileName, 'w')
		csvFile = csv.writer(f)
		csvFile.writerow(["Category Name", "Registered Users"])

		for c in self.categoryList: 
			csvFile.writerow([c["name"], c["count"]])
		f.close()

if __name__ == '__main__':
	pushioAPI = API("Your App ID", "Your Service Secret", debug=True)
	
	testNotification = Notification(message="Hello, Test World")
	pushioAPI.sendTestDevicePushNotification(testNotification)
	
	notification = Notification(message="Hello, Entire World")
	pushioAPI.sendBroadcastPushNotification(notification)

	notification = Notification(message="Hello, Sports World")
	categories = "Sports"
	pushioAPI.sendCategoryPushNotification(notification, categories)
	
	notification = Notification(message="Hello, Sports or US World")
	categories = "Sports or US"
	pushioAPI.sendCategoryPushNotification(notification, categories)

	apns = APNS(alert="Hello, iOS World", sound="beep.wav")
	notification = Notification(message="Hello, Entire World", payload_apns=apns.payload)
	pushioAPI.sendBroadcastPushNotification(notification)
	
	pushioAPI.sendNewsstandContentAvailablePushNotification()
	
	notification = Notification(message="Hello, Sports in 5 minutes from now")
	categories = "Sports"
	pushioAPI.sendCategoryPushNotification(notification, categories, deliver_at=pushioAPI.secondsFromNow(5*60))
	
	
