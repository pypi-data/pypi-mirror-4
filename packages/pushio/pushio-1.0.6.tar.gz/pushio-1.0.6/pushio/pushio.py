#!/usr/bin/env python
# encoding: utf-8
"""
pushio.py

Copyright (c) 2012 Push IO LLC. All rights reserved.
"""

import sys
import os
import urllib
import json

PUSHIO_API_ENDPOINT = "https://manage.push.io"
PUSHIO_API_VERSION = "v1"

class API:
	def __init__(self, appID, senderSecret, customEndpoint=None, debug=False):
		"""This is the object that you should create to send API requests to Push IO"""
		
		if appID == None or len(appID) == 0 or \
			senderSecret == None or len(senderSecret) == 0 or \
			appID == "Your App ID" or senderSecret == "Your Sender Secret":
			raise Exception("You must init this class with your App ID and Sender Secret")
		
		self.appID = appID
		self.senderSecret = senderSecret
		
		self.customEndpoint = customEndpoint
		self.debug = debug
					
	def sendBroadcastPushNotification(self, notification):
		params = {
			"payload" : notification.json,
			"audience" : "broadcast"
		}
		self.post("notify_app", params)
		
	def sendTestDevicePushNotification(self, notification):
		params = {
			"payload" : notification.json,
		}
		self.post("test_app", params)

	def sendCategoryPushNotification(self, notification, categories):
		params = {
			"payload" : notification.json,
			"tag_query" : categories
		}
		self.post("notify_app", params)
		
	def sendNewsstandContentAvailablePushNotification(self):
		apns = APNS(aps_extra={"content-available":1})
		notification = Notification(payload_apns=apns.payload)
		
		params = {
			"payload" : notification.json,
			"audience" : "broadcast"
		}
		self.post("notify_app", params)
			
	def endpoint(self, handler):
		if self.customEndpoint:
			apiURL = self.customEndpoint
		else:
			apiURL = PUSHIO_API_ENDPOINT
		return "%s/api/%s/%s/%s/%s" %(apiURL, PUSHIO_API_VERSION, handler, self.appID,self.senderSecret)
		
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
				print "%d success\n" %(status.code)
		else:
			print "===Push IO API response==="
			print "%d failure\n" %(status.code)


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
						props_to_clear=None):
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
	
	
