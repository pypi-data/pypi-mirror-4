#!/usr/bin/env python
# encoding: utf-8

# from django.core.context_processors import csrf
# from international.views import *  TODOMAS

# @csrf_exempt
def requestEmail(request):
	try:
		ms = MailSubscription.objects.get(user=request.user.id)
		email = ms.destination_email
		period =ms.period
	except:
		period = "never"	
		# Get the mail address if the current user is related to a client and doesnt have subscriptions yet
		# try:  TODOMAS
		# 	email = Client.objects.get(user=request.user.id).email
		# 	if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None: raise
		# except:
		email =""
	return email,period

# @user_ok
# @csrf_exempt
def save_subscription_settings(request):
	usr = User.objects.get(id=request.user.id)
	if 'email' in request.POST and 'period' in request.POST:
		email = request.POST['email']
		period = request.POST['period']
		# if there is no addres or is not valid, try to get the address from the client
		if email == None or re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:

			t = Template('KO: not valid email address')
			return HttpResponse(t.render(RequestContext(request)))
		# Check that the period is vaid
		if period in ('day','week','fifteen','month','never'):
			try:
				ms = MailSubscription.objects.get(user=usr)
				ms.delete()
			except:
				pass
			try:
				ms	= MailSubscription(period=period,destination_email=email,user=usr,created_by=usr)
				ms.save()
			except:
				t = Template('KO: Could not save the subscription settings pat')				
		else:
			t = Template('KO: Incorrect parameters')
	else:
		t = Template('KO: Incorrect parameters')
	
	t = Template('OK: Settings updated, message sent')
	
	sendmail(request,'subscription_changed',email)
	
	return HttpResponse(t.render(RequestContext(request)))
	

def sendmail(request,code,to):
	from_field = settings.DEFAULT_FROM_EMAIL

	mails ={
		'subscription_changed': ['[MyRealStats] Mail subscription changed', 'Your mail CDR subscription has been successfully updated to the new settings']
	}
	if code in mails:
		status = send_mail(mails[code][0],mails[code][1], from_field,[to], fail_silently=False)

	else: 
		return 0
		
	return status