This module makes it simple to send push notifications via Push IO's push notification service.

You can install it with your favorite python package manager:

	pip install pushio

In order to use this module, you need to have an account with Push IO (https://manage.push.io) and have an
app setup.

It's really simple to get started. Just have your App ID and Service Secret handy and substitute
the placeholders with them when creating the API object.

	from pushio import pushio

	pushioAPI = pushio.API("Your App ID", "Your Service Secret", debug=True)

Then, create a Notification object and determine how you want to send–– test device, broadcast, or category push notifications.
	
	testNotification = pushio.Notification(message="Hello, Test World")
	pushioAPI.sendTestDevicePushNotification(testNotification)
	
	notification = pushio.Notification(message="Hello, Entire World")
	pushioAPI.sendBroadcastPushNotification(notification)

	notification = pushio.Notification(message="Hello, Sports World")
	categories = "Sports"
	pushioAPI.sendCategoryPushNotification(notification, categories)
	
	notification =pushio. Notification(message="Hello, Sports or US World")
	categories = "Sports or US"
	pushioAPI.sendCategoryPushNotification(notification, categories)

If your app is an iOS Newsstand app, you can initial background content update downloads this way:

	pushioAPI.sendNewsstandContentAvailablePushNotification()

You can even do complex things like pass platform specific values, with each other platform getting the Notification object values.

	apns = pushio.APNS(alert="Hello, iOS World", sound="beep.wav")
	notification = pushio.Notification(message="Hello, Entire World", payload_apns=apns.payload)
	pushioAPI.sendBroadcastPushNotification(notification)

There is much more you can do. Please check out our docs site (http://docs.push.io), our support system (https://pushio.zendesk.com), or our irc channel (#pushio on irc.freenode.net).


